import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_keys import keys
from threading import Thread

from multipledispatch import dispatch

def get_w3(url):
    w3 = Web3(Web3.HTTPProvider(url))
    print("Blockchain Connection:",w3.isConnected())
    if w3.isConnected():
        if web3.__version__.split(".")[0] == "4":
            w3.middleware_stack.inject(geth_poa_middleware,layer=0)
        else:
            w3.middleware_onion.inject(geth_poa_middleware,layer=0)
    else:
        assert False, "No connection"

    return w3

@dispatch(str)
def get_key_pair(private_key):
    private_key = Web3.toBytes(int(private_key,16))
    public_address = keys.PrivateKey(Web3.toBytes(private_key)).public_key.to_checksum_address()
    return public_address, private_key

@dispatch(str,str)
def get_key_pair(dir_password,dir_keystore):
    with open(dir_password) as f:
        password=f.read().strip()

    with open(dir_keystore,"r") as keyfile:
        encrypted_key = keyfile.read()
        private_key = web3.eth.Account.decrypt(encrypted_key, password)
    public_address = keys.PrivateKey(private_key).public_key.to_checksum_address()
    print("public_address",public_address)
    print("private_key",private_key)
    return public_address,private_key

def sign_transaction(w3,function,data,public_address,private_key,nonce):
    transaction = function(*data).buildTransaction({
        "from": public_address,
        "nonce": nonce})   
    signed = w3.eth.account.sign_transaction(transaction,private_key)
    return signed.rawTransaction
# ------------------------------------------------------------------------------------------------ #
# Time Travel
# ------------------------------------------------------------------------------------------------ #

def time_travel(w3,seconds):
    result = w3.provider.make_request("evm_increaseTime",[seconds])
    assert "result" in result, result['error']['message']
# ------------------------------------------------------------------------------------------------ #
# Check whether transactions successful
# ------------------------------------------------------------------------------------------------ #
def has_tx_successful(tx_receipt):
    status = tx_receipt.get("status",None)
    if status == 1:
        return True
    if status == 0:
        print("*"*50)
        print(tx_receipt)
        print("*"*50)
        return False


def receipt_getter(w3,tx_hash,tx_receipts,timeout=100):
    try:
        tx_receipts[tx_hash] = w3.eth.waitForTransactionReceipt(tx_hash,timeout)
    except web3._utils.threads.Timeout:
        pass

def get_receipts_multithreaded(w3,tx_hashes,timeout=100):
    # one thread per transaction
    tx_receipts = {}
    threads = []
    for tx_hash in tx_hashes:
        t = Thread(target = receipt_getter,args=(w3,tx_hash,tx_receipts,timeout)) 
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    # print(tx_receipts)
    return tx_receipts

def check_transaction_successful(w3,tx_hashes,sample_size = 50, timeout = 100):
    print("check transaction successfulness")
    tx_hashes_batch_size = 50
    tx_receipts = {}
    for i in range(0,len(tx_hashes),tx_hashes_batch_size):
        tx_hashes_batch = tx_hashes[i:i+tx_hashes_batch_size]
        tx_receipts_batch = get_receipts_multithreaded(w3,tx_hashes_batch)
        tx_receipts = {**tx_receipts,**tx_receipts_batch}
    print("*"*50)
    if len(tx_hashes) == len(tx_receipts):
        print(f"Good: No timeout, received the receipts for all {len(tx_hashes)} transactions.")
    else:
        print(f"Bad: Timeout, received receipts only for {len(tx_receipts)} out of {len(tx_hashes)} transactions.")
    print("*"*50) 
    bad_counter = 0
    min_block_number = float('inf')
    max_block_number = 0
    for tx_hash, tx_receipt in tx_receipts.items():
        if not has_tx_successful(tx_receipt):
            bad_counter+=1
        tmp = tx_receipt.get("blockNumber",None)
        max_block_number = max(max_block_number,tmp)
        min_block_number = min(min_block_number,tmp)
    block_different = max_block_number-min_block_number+1
    print(f"Block start: {min_block_number} Block end: {max_block_number} Total block: {block_different}")

    print("*"*50) 
    if bad_counter:
        print(f"Bad: {bad_counter} out of {len(tx_receipts)} not successful!")
    else:
        print(f"Good: All {len(tx_receipts)} transactions successful!")
    print("*"*50) 

    return bad_counter

