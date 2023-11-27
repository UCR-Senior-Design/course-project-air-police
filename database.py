import sys
sys.path.append('../')
import os
from dotenv import load_dotenv
from data_call import dc
from pymongo import MongoClient
import pandas as pd
load_dotenv()
# connection = os.environ['c_URI']
# client = MongoClient(connection)
# db = client["SSProject"]
# collection = db["Devices"]

# testing code
# post = {"_id": 1, "SerialNumber": "test", "pm25": 10.5, "pm10": 12.5}
# collection.insert_one(post)
# add schemas here probably

def connect():
    connection = os.environ['c_URI']
    client = MongoClient(connection)
    db = client["SSProject"]
    collection = db["Devices"]
    return db, collection


def pushDB(data):
    #####################################################################
    # pushes data into the database                                     #
    # Parameters:                                                       #
    #   data: pandas dataframe from fetchData() check data.py           #
    #   schemas: the specific schema/ dictionery to upload data         #
    #       Default: name is probably gonna be schema which stores in   #
    #           the default columns of sn lon lat pm25 pm10 timestamp   #
    # Return:                                                           #   
    #####################################################################
    db, collection = connect()
    # newDict = schemas
    # keyList = list( newDict.keys())
    
    for i, rdata in data.iterrows():
        nd = rdata
        newDict = nd.to_dict()
        newDict['_id'] = i
        collection.insert_one(newDict)
        
        # for j in keyList:
        #     if j == "_id":
        #         continue
        #     #need to add error catching here
        #     newDict[j] = rdata[j]

        # collection.insert_one(newDict)
    return

def pullData():
    ######################################################################
    # pulls all data from database                                       #
    # PARAMETERS:                                                        #
    # Return:                                                            #
    #   data: returns a dson/ dataframe/ list / dataframe  of the data   #
    ######################################################################
    db, collection = connect()
    datas = collection.find()
    data = pd.DataFrame(datas)
    return data

def updateData(serialNumber, newData):
    ######################################################################
    # updates the data of a specific database                            #
    # Parameters:                                                        #
    #   serialNumber: the serial number of the device needs updating     #
    #   newData: dictionary of the new data needed                       #
    # Return:                                                            #
    ######################################################################
    db, collection = connect()
    ## need to add some error checking to make sure keys match with previous data
    keys = list(newData.keys())
    for i in range(0, len(keys)):
        collection.update({"sn": serialNumber},
                          {"$set": {
                              keys[i]:newData[i] 
                          }})
    return

def updateAllData(columns):
    ######################################################################
    # updates everything                                                 #
    # Parameters:                                                        #
    # Return:                                                            #
    ######################################################################
    data = dc.fetchData(columns)
    for i, nd in data.iterrows():
        updateData(nd["sn"], nd)
    return

data = dc.fetchData()
pushDB(data)
print(pullData())