import web3
from web3 import Web3

from web3.middleware import geth_poa_middleware
from eth_keys import keys

from solcx import compile_files,get_solc_version,get_installed_solc_versions,set_solc_version,install_solc
import json
import sys
sys.path.insert(1,"../00_utils/")
from utils import get_w3,get_key_pair

install_solc('0.6.9')

print("Current solc version:",get_solc_version())
print("Installed solc version:",get_installed_solc_versions())

url = "http://127.0.0.1:8545"
w3 = get_w3(url)

# public_address,private_key = get_key_pair("../poa-network/node/password.txt","../poa-network/node/keystore/UTC--2020-08-26T15-38-33.327660999Z--9e74086457814b6d7a87da12f000c6a91637784a")
public_address, private_key = get_key_pair("0x67f549fdaf5e0173cb71fcc6dd66a19aac0e63c5a09acb287007dd98b0571f51")
print("total balance",w3.eth.getBalance(public_address))  

set_solc_version('0.6.9')
contracts = compile_files(["./cattle.sol"])
deployment_compiled = contracts["./cattle.sol:Cattle"]
with open("abi.txt","w") as f:
    json.dump(deployment_compiled['abi'],f)
with open("bytecode.txt","w") as f:
    f.write(deployment_compiled['bin'])

deployment = w3.eth.contract(abi = deployment_compiled['abi'],bytecode = deployment_compiled['bin'])
estimate_gas = deployment.constructor().estimateGas(transaction=None)
print(f'gas: {estimate_gas:,}')
print(f'ether: {estimate_gas*0.000000001:,}')
print(f'USD: {estimate_gas*0.000000001*240:,}')


transaction = deployment.constructor().buildTransaction({"from":public_address,"nonce":w3.eth.getTransactionCount(public_address)})
signed = w3.eth.account.sign_transaction(transaction, private_key)   
tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

print(tx_receipt)


print("Contract Address:",tx_receipt.contractAddress)

print(f"actual gas used: {tx_receipt['gasUsed']:,}")

with open("contracts.txt","w") as f:
    f.write(tx_receipt.contractAddress)





