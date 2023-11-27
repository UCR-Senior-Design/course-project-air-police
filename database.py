import sys
sys.path.append('../')
import os
from dotenv import load_dotenv
from data_call import data as dc
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
    connection = os.environ['c_URI'] or os.eviron['DATABASE_URL'].to_str()
    client = MongoClient(connection)
    db = client["SSProject"]
    collection = db["Devices"]
    return db, collection

#works like a charm
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
        
        #add try and catch
        nd = rdata
        newDict = nd.to_dict()
        newDict['_id'] = i
        # this should check if the serial number already exists
        #if it does update the data instead
        if newDict['sn'] == collection.find({'sn':newDict['sn']}):
            print("data already stored calling update()")
            updateData(newDict['sn'],newDict)
            continue
        #iterates through the collection to find the next available _id
        while i != collection.find({'_id':i}):
            i += 1
        #adds
        newDict['_id'] = i
        collection.insert_one(newDict)
        
        # for j in keyList:
        #     if j == "_id":
        #         continue
        #     #need to add error catching here
        #     newDict[j] = rdata[j]

        # collection.insert_one(newDict)
    return


#tested and works
def pullData(serialNumber=None):
    ######################################################################
    # pulls all data from database                                       #
    # PARAMETERS:                                                        #
    # Return:                                                            #
    #   data: returns a dson/ dataframe/ list / dataframe  of the data   #
    ######################################################################
    db, collection = connect()
    if serialNumber != None:
        datas = collection.find({'sn':serialNumber})
        data = pd.DataFrame(datas)
        return data
    else:
        datas = collection.find()
        data = pd.DataFrame(datas)
        return data

#works
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
    for i,data in enumerate(newData):
        collection.update_one({"sn": serialNumber},
                          {"$set": {
                             keys[i]:newData[keys[i]]
                          }})
        # 
    return

#works but really slow
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
# pushDB(data)
# print(pullData())
print(pullData('MOD-PM-00711'))

# newDict = {
#     'pm25': 255,
#     'pm10': 255,
#     'timestamp':'2023-11-27T00:05:22'
# }
# updateData('MOD-PM-00645',newDict)
# print(pullData())

# updateAllData(['sn','pm25','pm10','timestamp'])
# print(pullData())
