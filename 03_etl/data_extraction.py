from web3 import Web3
import json
import random
import time
import web3
import asyncio

from utils import get_w3,get_key_pair,sign_transaction,check_transaction_successful,time_travel

# ------------------------------------------------------------------------------------------------ #

url = "http://127.0.0.1:8545"
w3 = get_w3(url)

with open("../02_contracts/contracts.txt","r") as f:
    contract_address = f.read()
with open("../02_contracts/abi.txt","r") as f:
    abi = f.read()   
contract = w3.eth.contract(address=contract_address,abi=abi)

# ------------------------------------------------------------------------------------------------ #
address_zero = "0x0000000000000000000000000000000000000000"
tokens = {}
def handle_event(event):
    # print(event)
    global tokens
    timestamp = w3.eth.getBlock(event.blockNumber).timestamp
    if event.args.tokenId not in tokens:
        tokens[event.args.tokenId]={}
    if event.event == "Transfer" and event.args["from"] == address_zero:
        tokens[event.args.tokenId]={"create_token":timestamp}
    elif event.event == "Transfer" and event.args.to == address_zero:
        tokens[event.args.tokenId]['deactive_token'] = timestamp
    elif event.event == "add_token_activity_event":
        tokens[event.args.token_id][event.args.token_activity[0]] = timestamp
 


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

def main():
    activity_filter = contract.events.add_token_activity_event.createFilter(fromBlock="latest",toBlock="latest")
    creation_filter = contract.events.Transfer.createFilter(fromBlock="latest",toBlock="latest")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(activity_filter,2),
                log_loop(creation_filter,2)
                ))
    except Exception as e:
        print(e)
    finally:
        loop.close()

if __name__ == '__main__':
    main()