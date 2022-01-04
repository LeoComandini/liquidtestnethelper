import argparse
import json
import os
import time

# pip install requests wallycore
import requests
import wallycore as wally
# must be installed from wheel
import greenaddress as gdk

def pp(j):
    print(json.dumps(j, indent=2))

def login(mnemonic):
    gdk.init({"datadir": os.getcwd()})
    s = gdk.Session({"name": "testnet-liquid"})
    s.login_user({}, {"mnemonic": mnemonic}).resolve()
    return s

def get_subaccounts(session):
    return session.get_subaccounts().resolve()['subaccounts']

def get_utxos(session, subaccount):
    utxos_per_asset = session.get_unspent_outputs({"subaccount": subaccount, "num_confs": 0}).resolve()['unspent_outputs']
    utxos = []
    for u in utxos_per_asset.values():
        utxos += u
    return utxos

def get_master_blinding_key(mnemonic):
    written, seed = wally.bip39_mnemonic_to_seed512(mnemonic, None)
    assert written == wally.BIP39_SEED_LEN_512
    return wally.asset_blinding_key_from_seed(seed)

def get_blinding_keypair(master_blinding_key, script):
    blinding_privkey = wally.asset_blinding_key_to_ec_private_key(master_blinding_key, script)
    blinding_pubkey = wally.ec_public_key_from_private_key(blinding_privkey)
    return blinding_privkey, blinding_pubkey

def get_address(session, subaccount, mnemonic, rpc):
    user_address = session.get_receive_address({"subaccount": subaccount}).resolve()
    master_blinding_key = get_master_blinding_key(mnemonic)
    blinding_privkey, blinding_pubkey = get_blinding_keypair(master_blinding_key, bytes.fromhex(user_address['blinding_script']))
    assert blinding_pubkey.hex() == user_address['blinding_key']
    # Import the address and blinding private key so core can unblind the user utxos
    rescan = False
    rpc.call('importaddress', user_address['address'], '', rescan)
    rpc.call('importblindingkey', user_address['address'], blinding_privkey.hex())
    witness_program = rpc.call('decodescript', user_address['script'])['segwit']['hex']
    p2sh = True
    rpc.call('importaddress', witness_program, '', rescan, p2sh)
    return user_address

def user_sign(session, subaccount, pset, blinding_nonces_str):
    utxos = get_utxos(session, subaccount)
    details = {"psbt": pset, "utxos": utxos}
    if blinding_nonces_str:
        details['blinding_nonces'] = blinding_nonces_str.split(',')
    return session.psbt_sign(details).resolve()

# copied from TODO
class RPCHost(object):

    def __init__(self, url):
        self._session = requests.Session()
        self._url = url

    def call(self, rpcMethod, *params):
        headers = {"content-type": "application/json"}
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        response = None
        for _ in range(5):
            try:
                response = self._session.post(self._url, headers=headers, data=payload)
            except requests.exceptions.ConnectionError as e:
                time.sleep(1)

        if response.status_code not in (200, 500):
            raise Exception(f"RPC connection failure: {response.status_code} {response.reason}")

        response_json = response.json()
        if "error" in response_json and response_json["error"] is not None:
            raise Exception(f"Error in RPC call: {response_json['error']}")

        return response_json["result"]

def get_rpc(url):
    return RPCHost(url)

def get_unspent(rpc):
    return rpc.call('listunspent')

def sat2btc(sat):
    return round(sat / 1e8, 8)

BTC_ASSET_ID = "144c654344aa716d6f3abcc1ca90e5641e4e2a7f633bc09fe3baf64585819a49"

def create_pset(rpc, inputs, outputs):
    inputs_ = []
    for i in inputs:
        txid, vout = i.split(':')
        inputs_.append({"txid": txid, "vout": int(vout), "sequence": 0xffffffff})

    outputs_ = []
    blinding_private_keys = []
    for o in outputs:
        t = o.split(':')
        if len(t) == 2:
            address, satoshi = t
            asset = BTC_ASSET_ID
        else:
            address, satoshi, asset = t

        satoshi = int(satoshi)
        o_ = {address: sat2btc(satoshi), 'asset': asset}
        bpk = None
        if address != 'fee':
            # To be able to return the blining nonces,
            # all output addresses must have private blinding keys known by the node
            # Those will later be used to get the blinding nonces.
            bpk = bytes.fromhex(rpc.call('dumpblindingkey', address))
            o_['blinder_index'] = 0
        outputs_.append(o_)
        blinding_private_keys.append(bpk)

    psbt = rpc.call('createpsbt', inputs_, outputs_)
    # blindpsbt
    sign = False
    psbt = rpc.call('walletprocesspsbt', psbt, sign)

    psbt_decoded = rpc.call('decodepsbt', psbt['psbt'])
    blinding_nonces = []
    for bpk, o in zip(blinding_private_keys, psbt_decoded['outputs']):
        bn = ''
        if bpk:
            ecdh_pubkey = bytes.fromhex(o['ecdh_pubkey'])
            bn = wally.sha256(wally.ecdh(ecdh_pubkey, bpk)).hex()
        blinding_nonces.append(bn)
    psbt['blinding_nonces'] = ','.join(blinding_nonces)
    return psbt

def node_sign(rpc, pset):
    return rpc.call('walletprocesspsbt', pset)

def combine(rpc, pset):
    return rpc.call('combinepsbt', pset) # list

def finalize(rpc, pset):
    ret = rpc.call('finalizepsbt', pset)
    assert ret['complete']
    tx = ret['hex']
    ret = rpc.call('testmempoolaccept', [tx])
    assert all(e['allowed'] for e in ret)
    return tx

def sendraw(rpc, tx):
    return rpc.call('sendrawtransaction', tx)


def main():
    parser = argparse.ArgumentParser("Helper to construct PSET with Elements and GDK")
    parser.add_argument("-m", "--mnemonic", help="The user GDK mnemonic")
    parser.add_argument("-s", "--subaccount", type=int, help="The user GDK subaccount")
    parser.add_argument("-n", "--node-url", help="The node url, http://user:pass@host:port/")

    subparsers = parser.add_subparsers(dest='command')
    
    parser_usersubaccounts = subparsers.add_parser("usersubaccounts", help="Get user subaccounts")
    parser_useraddress = subparsers.add_parser("useraddress", help="Get user address and import as watch only for the node")
    parser_userutxos = subparsers.add_parser("userutxos", help="Get user utxos")
 
    parser_nodeutxos = subparsers.add_parser("nodeutxos", help="Get node utxos")

    parser_createpset = subparsers.add_parser("createpset", help="Create a blinded pset")
    parser_createpset.add_argument('--input', action='append', help='TXID:VOUT')
    parser_createpset.add_argument('--output', action='append', help='ADDRESS:SATOSHI:ASSET')

    parser_nodesign = subparsers.add_parser("nodesign", help="Sign a PSET with the node")
    parser_nodesign.add_argument('--pset', required=True)

    parser_usersign = subparsers.add_parser("usersign", help="Sign a PSET with the user")
    parser_usersign.add_argument('--pset', required=True)
    parser_usersign.add_argument('--blinding-nonces', help='Must be specified if signing inputs from AMP subaccounts. BLINDINGNONCE,BLINDINGNONCE,... a blinding nonce might be empty if the output is unblinded')

    parser_combine = subparsers.add_parser("combine", help="Combine PSETs")
    parser_combine.add_argument('--pset', required=True, action='append')
    
    parser_finalize = subparsers.add_parser("finalize", help="Finalize a PSET")
    parser_finalize.add_argument('--pset', required=True)

    parser_sendrawtx = subparsers.add_parser("send", help="Send a raw transaction")
    parser_sendrawtx.add_argument('--tx', required=True)

    args = parser.parse_args()
    if args.command == 'usersubaccounts':
        s = login(args.mnemonic)
        pp(get_subaccounts(s))
    elif args.command == 'userutxos':
        s = login(args.mnemonic)
        pp(get_utxos(s, args.subaccount))
    elif args.command == 'useraddress':
        s = login(args.mnemonic)
        rpc = get_rpc(args.node_url)
        pp(get_address(s, args.subaccount, args.mnemonic, rpc))
    elif args.command == 'nodeutxos':
        rpc = get_rpc(args.node_url)
        pp(get_unspent(rpc))
    elif args.command == 'createpset':
        rpc = get_rpc(args.node_url)
        pp(create_pset(rpc, args.input, args.output))
    elif args.command == 'nodesign':
        rpc = get_rpc(args.node_url)
        pp(node_sign(rpc, args.pset))
    elif args.command == 'usersign':
        s = login(args.mnemonic)
        rpc = get_rpc(args.node_url)
        pp(user_sign(s, args.subaccount, args.pset, args.blinding_nonces))
    elif args.command == 'combine':
        rpc = get_rpc(args.node_url)
        pp(combine(rpc, args.pset))
    elif args.command == 'finalize':
        rpc = get_rpc(args.node_url)
        pp(finalize(rpc, args.pset))
    elif args.command == 'send':
        rpc = get_rpc(args.node_url)
        pp(sendraw(rpc, args.tx))

if __name__ == "__main__":
    main()
