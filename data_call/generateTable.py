# exclusivly generates the researcher table
import json
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

apiKey = os.environ['api_key']

def fetchData(columns = ['sn','pm25','pm10', 'timestamp']):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        columns: list of columns the data should return                           ##
    ##             default: ['sn','pm25','pm10','timestamp']       ##
    ## Output:                                                                          ##
    ##        data: json file with  the sensor data                ##
    ######################################################################################

     # apiKey
    auth = HTTPBasicAuth(apiKey,"")
    #uses requests to get data from our network
    # uses try except for error handling
    try:
        req = requests.request("get","https://api.quant-aq.com/device-api/v1/data/most-recent/?network_id=9", headers = None, auth = auth)
    except:
        print("Error Incorrect API Key")
        return None


    #loads the request into a json formatt
    djson = req.json()
    #filters data for specific columns
    edata = {col: [] for col in columns}
    ##loops through all entries in djson data section
    for entry in djson["data"]:
        for col in columns: 
            # since geo location is given in a list, this check is needed for our data to work properly
            if col == "geo.lat":
                edata[col].append(entry['geo']['lat'])
            elif col == "geo.lon":
                edata[col].append(entry['geo']['lon'])
            else:
                edata[col].append(entry[col])

    # write to json file
    with open('data_call/table.json', 'w') as file:
        json.dump(edata, file)

    # prints after converting dictionary to dataframe object
    #print(pd.DataFrame(edata))

fetchData()