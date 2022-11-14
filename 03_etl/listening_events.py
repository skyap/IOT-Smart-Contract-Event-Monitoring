import web3
from web3 import Web3
from datetime import datetime
import asyncio
from utils import get_w3,get_key_pair,sign_transaction,check_transaction_successful

url = "http://127.0.0.1:8545"
w3 = get_w3(url)

directory = '../02_contracts/'
with open(directory+"contracts.txt","r") as f:
    contract_address = f.read()
with open(directory+"abi.txt","r") as f:
    abi = f.read()
contract = w3.eth.contract(address=contract_address,abi=abi)

def handle_event(event):
    # print(w3.eth.getBlock(event.hex()).number)
    print(event)
    print(datetime.fromtimestamp(w3.eth.getBlock(event.blockNumber).timestamp))
    # and whatever

async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        await asyncio.sleep(poll_interval)

def main():
    # block_filter = w3.eth.filter('latest')
    # tx_filter = w3.eth.filter('pending')
    # event_filter = w3.eth.filter({"address": "0xF4C53fb1134Bc69fE0deF1fe3A47C05E82f5F3bb"})
    activity_filter = contract.events.add_token_activity_event.createFilter(fromBlock="latest",toBlock="latest")
    creation_filter = contract.events.Transfer.createFilter(fromBlock="latest",toBlock="latest")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2),
                # log_loop(event_filter,2)
                log_loop(activity_filter,2),
                log_loop(creation_filter,2)
                ))
    except Exception as e:
        print(e)
    finally:
        loop.close()

if __name__ == '__main__':
    main()