from web3 import Web3
import json
import random
import time
import web3
import string
import numpy as np

import sys
sys.path.insert(1,"../00_utils/")

from utils import get_w3,get_key_pair,sign_transaction,check_transaction_successful,time_travel


url = "http://127.0.0.1:8545"
w3 = get_w3(url)

with open("contracts.txt","r") as f:
    contract_address = f.read()
with open("abi.txt","r") as f:
    abi = f.read()

contract = w3.eth.contract(address=contract_address,abi=abi)


# def token_activity():
#     activity_data = {}
#     for i in range(random.randint(1,10)):
#         activity_data[i] = random_text(random.randint(1,10))

#     return [str(f"{i},{v}") for i,v in activity_data.items()]

# sample_list = ["activity "+str(i) for i in range(100)]
# def token_activity():
#     return random.sample(sample_list,random.randint(1,10))

# print(random_text(10))
# print(token_type())
# print(token_external_id())
# print(token_detail())
# print(token_activity())
# exit()


p_new_token = 0.5
p_update_token_activity = 0.45
p_deactivate_token = 0.05
processes_probability_distribution = [p_deactivate_token,p_update_token_activity,p_new_token]

action = lambda : np.random.choice(["deactive_token","add_token_activity","create_token"], 1,p=processes_probability_distribution)
token_id = contract.functions._tokenId().call()+1

token_id_list = []


tpb = lambda : random.randint(1,10)
delay_between_block = 5

public_address, private_key = get_key_pair("0x67f549fdaf5e0173cb71fcc6dd66a19aac0e63c5a09acb287007dd98b0571f51")

nonce = w3.eth.getTransactionCount(public_address)

token_activity = {}
# for i in range(10):
#     print(action())
# exit()
for i in range(5000):
    current_tpb = tpb()
    start_time = time.time()
    tx_hashes = []
    current_token = []
    for j in range(current_tpb):
        print(i,j,end=" ")
        k = action()[0]
        if k == "create_token" or len(token_id_list) == 0: 
            k = "create_token"
            # print("here")
            current_token.append(token_id)        
            # token_id_list.append(token_id)
            signed_rawTransaction = sign_transaction(w3,contract.functions.create_token,[],public_address,private_key,nonce)
            tx_hashes.append(w3.eth.sendRawTransaction(signed_rawTransaction))
            print(k, end="=>")
            print("token_id",token_id)
            token_id+=1
        elif k == "deactive_token":
            token = random.choice(token_id_list)
            print(k, end="=>")
            print("token_id",token)
            signed_rawTransaction = sign_transaction(w3,contract.functions.deactive_token,[token],public_address,private_key,nonce)
            tx_hashes.append(w3.eth.sendRawTransaction(signed_rawTransaction))
            token_id_list.remove(token)
        elif k == "add_token_activity":
            token = random.choice(token_id_list)
            if token not in token_activity:
                token_activity[token] = 0
            # ------------------------------------------------------------------------------------------------ #
            new_token_activity = ["activity "+str(token_activity[token])]
            token_activity[token]+=1
            # ------------------------------------------------------------------------------------------------ #

            # current_count = token_activity[token]
            # new_count = random.randint(1,10)+current_count
            # new_token_activity = ["activity "+str(i) for i in range(current_count,new_count)]
            # token_activity[token]+=new_count
            # ------------------------------------------------------------------------------------------------ #

            # print(k, end="=>")
            # print("token_id",token)
    
            signed_rawTransaction = sign_transaction(w3,contract.functions.add_token_activity,[token,new_token_activity],public_address,private_key,nonce)
            tx_hashes.append(w3.eth.sendRawTransaction(signed_rawTransaction))

        nonce+=1

    # Check successful transaction
    check_transaction_successful(w3,tx_hashes,timeout=1000)
    # wait until block is sealed
    while time.time()-start_time<=5:
        continue
    if random.random()>0.1:
        # print("Time Travel for 1 day")
        time_travel(w3,1*24*3600)
    token_id_list+=current_token








