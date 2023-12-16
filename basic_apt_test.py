#https://quant-aq.github.io/py-quantaq/ library documentation

# imports required to use the api
import quantaq
from quantaq.utils import to_dataframe
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json

# input unique apikey here
apiKey = '7QQN18AOIHAA15UD9SNKUIA1'


#updates the list of devices in the area. 
def update():
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


# function that returns SN, particle count, and coordinates of devices passed in
def fetchSensorData(client, sn):
    data = []
    # appends raw data of each sensor in sn to a list
    for i in sn:
        data.append( to_dataframe(client.data.list( sn = i, sort="timestamp,desc", limit=1 ) ) )

    # format and return necessary data
    data = pd.concat(data, ignore_index=True)
    data = data[['sn', 'pm10','pm25', 'geo.lat', 'geo.lon']]
    return data


# driver function
def main():
    # get the client
    client = quantaq.QuantAQAPIClient(api_key = apiKey)

    # update the list of serial numbers and call function that prints data
    sn = update()
    print (fetchSensorData(client, sn))

main()
