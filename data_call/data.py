#https://quant-aq.github.io/py-quantaq/ library documentation
# eventually put this into a class
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta
#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.
apiKey = os.environ['api_key']
mapKey = os.environ['map_key']


def fetchData(columns = ['geo.lat', 'geo.lon','sn','pm25','pm10', 'timestamp']):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        columns: list of columns the data should return                           ##
    ##             default: ['geo.lat', 'geo.lon','sn','pm25','pm10','timestamp']       ##
    ## Output:                                                                          ##
    ##        data: dataframe of the retrieved data                                     ##
    ######################################################################################

    # apiKey
    auth = HTTPBasicAuth(apiKey,"")
    #uses requests to get data from our network
    req = requests.request("get","https://api.quant-aq.com/device-api/v1/data/most-recent/?network_id=9", headers = None, auth = auth)
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
    #converts dictionary to dataframe object
    data = pd.DataFrame(edata)
    return data


#find devices that are not outputting a pm2.5 or pm10 reading
def notFunctional(data=fetchData(['geo.lat', 'geo.lon', 'sn', 'pm25', 'pm10', 'timestamp'])):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        data: current data to find non functional                                 ##
    ##            data must include 'sn', 'pm25', 'pm10', and 'timestamp' columns       ##
    ## Output:                                                                          ##
    ##        nf: dataframe of the list of sn, reason, and index                        ##
    ##            indicates there is a problem with the device                          ##
    ######################################################################################
    # added try
    nonFunc = []
    reason = []
    ind = []
    for index, row in data.iterrows():
        try:
            Ti = row['timestamp'].index(" ")
            t = row['timestamp'][::Ti] + ' ' + row['timestamp'][Ti + 1::]
            timestamp = datetime.strptime(t, '%y%m%d %H:%M:%S')  # Adjusted the timestamp format
        except ValueError:
            # Handle the case where the space character is not found in the timestamp
            timestamp = datetime.now()  # You might want to set it to an appropriate default value

        todays = datetime.today()
        todays = todays - timedelta(days=2)
        ##checks if the data is outdated
        if timestamp < todays:
            ind.append(index)
            nonFunc.append(row['sn'])
            reason.append('data too old')
        ##checks if the data does not display properly
        ## NOTE: we may change to check if there was a properly read data recently.  but currently just current data.
        if pd.isna(row['pm25']) or pd.isna(row['pm10']):
            if row['sn'] not in nonFunc:
                ind.append(index)
                reason.append('pm2.5 or pm10 is not reading properly')
                nonFunc.append(row['sn'])
    nf = pd.DataFrame({'index': ind, 'sn': nonFunc, 'reason': reason})
    return nf



def toJson(data,fileName="temp.json"):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        data: current data to find non functional                                 ##
    ## Output:                                                                          ##
    ##        jf: json file                                                             ##
    ######################################################################################

    ## shit box code will fix later but currently works. have a better version of writing to a json file. but currently do not feel like porting over.
    datas = data.fillna('null')
    db = datas.to_dict(orient='records')
    with open(fileName, 'w') as f:
        json.dump(db,f)
    # d = datas.to_dict(orient='records')
    # length = len(d)
    # pos = 1
    # with open(fileName, 'w') as f:
    #     f.write('[\n')
    #     for record in d:
    #         json.dump(record, f)
    #         if pos == length:
    #             f.write('\n')
    #         else:
    #             f.write(',\n')
    #         pos += 1
    #     f.write(']')

#generate heat map function
## might move this to javascript
#https://developers.google.com/maps/documentation/javascript/