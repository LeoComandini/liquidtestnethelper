# Test partial signing

Get user address:
```
$ python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL useraddress
{
  "address": "vjU2A6NohNAKsPWyBwzgQg52KR6zxMisTVip6XAuz5s6ABxeWhCBAsgw1ENKSKrEYAiKyqn6bes8iLrg",
  "address_type": "p2wsh",
  "blinding_key": "030ebb3ab0df112d17c7e7e8f4f44c6e61904ec0ed4c4c5938db33d79f0db02d97",
  "blinding_script": "a914f9838810e9306df372f0ea3107bb5cea3ed8367f87",
  "branch": 1,
  "is_blinded": true,
  "pointer": 30,
  "script": "522103ec7212ec61fc5d1e98394412e1c9cacd696e8fca695521027309644b8297b2d92103e04a9e6e9129cddcf65d4319e02de76f2853c82790d71316a4b06a03cefe7b6752ae",
  "script_type": 14,
  "subaccount": 1,
  "subtype": null,
  "unblinded_address": "93AmXoJayfvMwKXoJVVXiTvuexGvuEt9To"
}
```
This also import the address and blinding private key in the node, which is necessary for the node to blind correctly a transaction including and input sent to such address.

Send some funds to that address and to the node (e.g. use https://liquidtestnet.com/faucet).

Check the user utxos:
```
$ python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL userutxos
[
  {
    "address_type": "p2wsh",
    "amountblinder": "af69ac8998103a1c00f454a38449c5e9b7f5f4413fde65535210f2363734532f",
    "asset_id": "144c654344aa716d6f3abcc1ca90e5641e4e2a7f633bc09fe3baf64585819a49",
    "asset_tag": "0b86231a1eea27ee01c5743215fc148233037b550020a7d825b5bd49145a10db50",
    "assetblinder": "72c460f663c90b348dc7d66ceba01c83501cb9ca12ad1b0d8a9be6e1eca3ff89",
    "block_height": 106961,
    "commitment": "083cf820fd8019790120acecdd4a953ec949065add497fb2b9f8abdd5c4ba99094",
    "confidential": true,
    "is_internal": false,
    "nonce_commitment": "0281fb93985ba6d570ac5ef17b567be1e0580bffd01531830cf559f8097d56e3f9",
    "pointer": 30,
    "pt_idx": 0,
    "range_proof": "603300000000
    "satoshi": 10000000,
    "script": "a914f9838810e9306df372f0ea3107bb5cea3ed8367f87",
    "script_type": 14,
    "subaccount": 1,
    "subtype": 0,
    "surj_proof": "0100016b12f3c52c5c5d1db1321848990e6528a5ead13ed069762f1a3589db12f4475ad374c34501064726189fd8fdf7d8d02d3308e62774ddc4626e3cc8b7d7122b88",
    "txhash": "eca5bccf48f15efc285d3e520076310a1b5594f1beecf62343569ef9b787c0da",
    "user_status": 0
  }
]
```


Check the node utxos:
```
$ python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL nodeutxos
[
  {
    "txid": "3072eb84e7ac3785af8ce44108e47100238711d9ecb9d34608e9edecd4f6f9bc",
    "vout": 1,
    "address": "tex1qwc5yh9sr9ywuvdv9f7q4rcfwdjul264yu2nl3e",
    "label": "",
    "scriptPubKey": "001476284b9603291dc635854f8151e12e6cb9f56aa4",
    "amount": 0.1,
    "assetcommitment": "0aca33110bd356678cc45021ee6a7965bb04d54909aba98b3291e55023d8b7cab7",
    "asset": "144c654344aa716d6f3abcc1ca90e5641e4e2a7f633bc09fe3baf64585819a49",
    "amountcommitment": "09429dfde76b0e45a444c263f2acdda267ffb72bd59fe45f0ba0c0fd574203b327",
    "amountblinder": "e038f6fe4636ebb055ca567942fa16aa4754ae254ef11af3cd0034161ed33a68",
    "assetblinder": "d20daf551d2daa36d61f1038af49c19fe1fced988648ee8ce308f487d50a6d4f",
    "confirmations": 91,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([bdd16acb/0'/0'/0']03bd58c53cba715696fb26bf83e37099b4d33523f428700e03eb16613d68bc8800)#xqadq28z",
    "safe": true
  },
  {
    "txid": "eca5bccf48f15efc285d3e520076310a1b5594f1beecf62343569ef9b787c0da",
    "vout": 0,
    "address": "93AmXoJayfvMwKXoJVVXiTvuexGvuEt9To",
    "label": "",
    "redeemScript": "002045a126e0b02a7d0874b3515d5a72f4052b686222931c7e6d1c715abeec376521",
    "scriptPubKey": "a914f9838810e9306df372f0ea3107bb5cea3ed8367f87",
    "amount": 0.1,
    "assetcommitment": "0b86231a1eea27ee01c5743215fc148233037b550020a7d825b5bd49145a10db50",
    "asset": "144c654344aa716d6f3abcc1ca90e5641e4e2a7f633bc09fe3baf64585819a49",
    "amountcommitment": "083cf820fd8019790120acecdd4a953ec949065add497fb2b9f8abdd5c4ba99094",
    "amountblinder": "af69ac8998103a1c00f454a38449c5e9b7f5f4413fde65535210f2363734532f",
    "assetblinder": "72c460f663c90b348dc7d66ceba01c83501cb9ca12ad1b0d8a9be6e1eca3ff89",
    "confirmations": 5,
    "spendable": false,
    "solvable": false,
    "safe": true
  }
]
```
Note that the 2nd utxo is the one owned by the user (`"spendable": false`, that is watch only)

Construct a blinded pset sending everything to the node (get one of its addresses):
```
TMPRET=$(python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL createpset --input 3072eb84e7ac3785af8ce44108e47100238711d9ecb9d34608e9edecd4f6f9bc:1 --input eca5bccf48f15efc285d3e520076310a1b5594f1beecf62343569ef9b787c0da:0 --output tlq1qqfd52j89ndy6775tjaf0q84k6tddwk7de7uv2m7490vgpp8z03e0tk24uefpvpr4axq7num55yth0gng9frtshv0haff5c6sf:19995000 --output fee:5000)
PSET=$(echo $TMPRET | jq -r .psbt)
BLINDINGNONCES=$(echo $TMPRET | jq -r .blinding_nonces)
```
Note that we have to balance the output and fee explicitly.

Node signs:
```
PSETNODE=$(python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL nodesign --pset $PSET | jq -r .psbt)
```

User signs:
```
PSETUSER=$(python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL usersign --pset $PSET  --blinding-nonces $BLINDINGNONCES | jq -r .psbt)
```

Node combines:
```
PSETCOMB=$(python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL combine --pset $PSETNODE --pset $PSETUSER | jq -r .)
```

Node finalizes:
```
TXFINAL=$(python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL finalize --pset $PSETCOMB | jq -r .)
```

Broadcast:
```
TXID=$(python liquidtestnethelper.py -m "$MNEMONIC" -s $SUBACCOUNT -n $NODEURL send --tx $TXFINAL | jq -r .)
echo $TXID
```
