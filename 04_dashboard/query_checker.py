import pymongo
import random
import pandas as pd
import pandas as pd 

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
    for d in collection_add_token_activity.find({},sort=[("token_id",pymongo.ASCENDING),("timestamp",pymongo.ASCENDING)]):
        token_id = str(d['token_id'])
        if d['token_id'] not in data:
            data[d['token_id']]={d['activity']:d['timestamp']}        
        else:
            data[d['token_id']][d['activity']] = d['timestamp']

       
    data = pd.DataFrame.from_dict(data).T
    col = data.columns.tolist()
    data = data[sorted(col)]
    
return data
