#https://quant-aq.github.io/py-quantaq/ library documentation
# eventually put this into a class
import quantaq
from quantaq.utils import to_dataframe
import numpy as np
import gmaps
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
from ipywidgets.embed import embed_minimal_html
from datetime import datetime, timedelta
#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.
apiKey = 'AOSIIFR5L7HM6KUISW2D4UFK'
mapKey = 'AIzaSyC3MDZ1-SOhalWrHhcz_o9WlgePVL_NYTI'
gmaps.configure(api_key=mapKey)
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
    #gets the list of serialnumbers from the retrieved data
    sn = data["data"][0]["devices"]
    #returns the list
    return sn
#return a df


def fetchData(client= quantaq.QuantAQAPIClient(api_key = apiKey), columns = ['geo.lat', 'geo.lon','sn','pm25','pm10', 'timestamp']):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        client: quantaq api client                                                ##
    ##        columns: list of columns the data should return                           ##
    ##             default: ['geo.lat', 'geo.lon','sn','pm25','pm10']                   ##
    ## Output:                                                                          ##
    ##        data: dataframe of the retrieved data                                     ##
    ######################################################################################
    devices = to_dataframe(client.devices.list())

    data = []
    # get every serial number from devices
    sn = update()
    
    # loop through each device and call data list limited to the most recent 1. 
    # NOTE: timestamp should be desc not asc in order to retrieve the most recent
    for i in sn:
        data.append(to_dataframe(client.data.list( sn = i, sort = "timestamp,desc", limit = 1 ) ) )
     

    #concat depreciated warning but works
    data = pd.concat(data, ignore_index=True)

    #filters out the columns to the columns we need
    data = data[columns]
    return data


#find devices that are not outputting a pm2.5 or pm10 reading
def notFunctional(client=quantaq.QuantAQAPIClient(api_key = apiKey), data = fetchData(quantaq.QuantAQAPIClient(api_key = apiKey))):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        client: quantaq api client                                                ##
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


#generate heat map function
## might move this to javascript
#https://developers.google.com/maps/documentation/javascript/heatmaplayer

def generateHeatMap(client, data, method):
    #######################################################################################################
    ## inputs: client: the quantaq apiclient                                                             ##
    ##        data: the data used to generate the heatmap. should be in geo.lat geo.lon pm25 pm10 format ##
    ##        method: indicates whether or not the heatmap displays pm25 or pm10                         ##
    ## what it should do:                                                                                ##
    ##        generate heatmap using the google map api if you can.                                      ##
    ## output:                                                                                           ##
    ##        create .png file                                                                           ##
    ## NOTES:                                                                                            ##
    ##        in the browser, to display the map on the site, just use map.png                           ##
    #######################################################################################################
    
    
    #rough attempt (Does not Work yet):
    #data = fetchData(client)
    # # print(data)
    # data = data.dropna(how='any')
    # print(data)
    # locations = data[['geo.lat', 'geo.lon']]
    # weight = data['pm25']
    # fig = gmaps.figure()
    # heatmap_layer = gmaps.heatmap_layer(locations, weights = weight)
    # fig.add_layer(heatmap_layer)

    return




#get the client

# client = quantaq.QuantAQAPIClient(api_key = apiKey)
# devices = to_dataframe(client.devices.list())
# data = fetchData(client)
# print(data)
# print(notFunctional(client, data))