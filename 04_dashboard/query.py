import pymongo
import random
import pandas as pd
import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def load_data():
    mongodb_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mongodb_client["blockchain"]

    collection_add_token_activity = db["add_token_activity_event"]

    collection_create_token = db["create_token_event"]
    collection_deactive_token = db["deactive_token_event"]
    # ------------------------------------------------------------------------------------------------ #

    total_token =  collection_create_token.find_one({},sort=[( '_id', pymongo.DESCENDING )])['token_id']
    total_deactive_token = collection_deactive_token.estimated_document_count()
    total_active_token = total_token - total_deactive_token

    print("total_token",total_token)
    print("total_deactive_token",total_deactive_token)
    print("total_active_token",total_active_token)


    data = {}
    for d in collection_create_token.find({}):
        data[d['token_id']] = {}
        data[d['token_id']]["create_token"] = d['timestamp']


    for d in collection_add_token_activity.find({},sort=[("token_id",pymongo.ASCENDING),("timestamp",pymongo.ASCENDING)]):
        data[d['token_id']][d['activity']] = d['timestamp']       

    for d in collection_deactive_token.find({}):
        data[d['token_id']]["deactive_token"]=d['timestamp']

    data = pd.DataFrame.from_dict(data).T
    col = data.columns.tolist()
    col = sorted(col,key=natural_keys)
    col = [col[-2]]+col[:-2]+[col[-1]]
    data = data[col]
    return data,total_token,total_deactive_token,total_active_token
