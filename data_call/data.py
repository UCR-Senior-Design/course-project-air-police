#https://quant-aq.github.io/py-quantaq/ library documentation
# eventually put this into a class
import numpy as np
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta
#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.
apiKey = 'AOSIIFR5L7HM6KUISW2D4UFK'
mapKey = 'AIzaSyC3MDZ1-SOhalWrHhcz_o9WlgePVL_NYTI'

#updates the list of devices in the area. 
def update():
    ######################################################################################
    ## Inputs:                                                                          ##
    ##                                                                                  ##
    ## Output:                                                                          ##
    ##        sn: list of all the serial numbers in our network                         ##
    ######################################################################################

    #note we have to use pythons request function b/c py-quantaq has not updated theirs for the new organizations quant aq update

    #passes in our api key
    auth = HTTPBasicAuth(apiKey,"")
    #uses requests to get our network
    req = requests.request("get","https://api.quant-aq.com/device-api/v1/orgs/1212/networks", headers = None, auth = auth)
    #loads the request into a json formatt
    data = req.json()
    print(data)
    #gets the list of serialnumbers from the retrieved data
    sn = data["data"][0]["devices"]
    #returns the list
    return sn
#return a df


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
def notFunctional(data = fetchData(['geo.lat', 'geo.lon','sn','pm25','pm10', 'timestamp'])):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        data: current data to find non functional                                 ##
    ##            data must include 'sn', 'pm25', 'pm10', and 'timestamp' columns       ##
    ## Output:                                                                          ##
    ##        nf: dataframe of the list of sn, reason, and index                        ##
    ##            indicates there is a problem with the device                          ##
    ######################################################################################
    nonFunc = []
    reason = []
    ind = []
    for index, row in data.iterrows():
        # print(row['pm25'])
        Ti = row['timestamp'].index("T")
        t = row['timestamp'][::Ti-1] + ' ' +  row['timestamp'][Ti+1::]
        timestamp = datetime.strptime(t,'%y-%m-%d %H:%M:%S')
        todays = datetime.today()
        todays = todays - timedelta(days = 2)
        ##checks if the data is outdated
        if row['timestamp'] < todays:
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
    nf = pd.DataFrame({'index': ind,'sn':nonFunc, 'reason': reason})
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