from web3 import Web3
import json
import random
import time
import web3
import pymongo
import asyncio
import sys
sys.path.insert(1,"../00_utils/")

from utils import get_w3,get_key_pair,sign_transaction,check_transaction_successful

directory = '../02_contracts/'
url = "http://127.0.0.1:8545"
w3 = get_w3(url)

# ------------------------------------------------------------------------------------------------ #

with open(directory+"contracts.txt","r") as f:
    contract_address = f.read()
with open(directory+"abi.txt","r") as f:
    abi = f.read()   
contract = w3.eth.contract(address=contract_address,abi=abi)


# -------------------------------------------- mongodb ------------------------------------------- #

mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongodb_client["blockchain"]

# ------------------------------------ mongodb sequence value ------------------------------------ #
# https://www.tutorialspoint.com/mongodb/mongodb_autoincrement_sequence.htm
collection_counters = db['counters']
if "counters" not in db.list_collection_names():
    
    mylist = [
        {"_id":"create_token_event","sequence_value":0},
        {"_id":"deactive_token_event","sequence_value":0},
        {"_id":"add_token_activity_event","sequence_value":0}

    ]
    collection_counters.insert_many(mylist)

def Sequence_Value(name):
    # print(name,collection_counters.find_one({"_id":name}))
    value = collection_counters.find_one({"_id":name})['sequence_value']
    collection_counters.update_one({"_id":name},{"$inc":{"sequence_value":1}})
    return value

# ------------------------------------------ Collections ----------------------------------------- #
# collection_create_token
# |id|token_id|timestamp|block_number|
# |int|int    |int      |int         |

# collection_deactive_token
# |id|token_id|timestamp|block_number|
# |int|int    |int      |int         |

# collection_add_token_activity
# |id|block_number|timestamp|token_id|activity|
# |int|array        |array      |int     |array|

collection_create_token = db["create_token_event"]
collection_deactive_token = db["deactive_token_event"]
collection_add_token_activity = db["add_token_activity_event"]


# --------------------------------------- Special function --------------------------------------- #
address_zero = "0x0000000000000000000000000000000000000000"
def handle_event(event):
    print(event)
    timestamp = w3.eth.getBlock(event.blockNumber).timestamp
    token_id = event.args.tokenId
    block_number = event.blockNumber
    if event.event == "Transfer" and event.args["from"] == address_zero:
        # event create_token_event
        # |id|token_id|timestamp|block_number|
        # |int|int    |int      |int         |
        token = {"_id":Sequence_Value("create_token_event"),"token_id":token_id,"timestamp":timestamp,"block_number":block_number}
        if token:
            collection_create_token.insert_one(token)

    elif event.event == "Transfer" and event.args.to == address_zero:
        # event deactive_token_event
        # |id|token_id|timestamp|block_number|
        # |int|int    |int      |int         |
        token = {"_id":Sequence_Value("deactive_token_event"),"token_id":token_id,"timestamp":timestamp,"block_number":block_number}
        collection_deactive_token.insert_one(token)
    elif event.event == "add_token_activity_event":
        # event collection_add_token_activity
        # |id|block_number|timestamp|token_id|activity|
        # |int|array        |array      |int     |array|
        activity = event.args.token_activity[0]
        token = {"_id":Sequence_Value("deactive_token_event"),"token_id":token_id,"activity":activity,"timestamp":timestamp,"block_number":block_number}
        collection_add_token_activity.insert_one(token)

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



