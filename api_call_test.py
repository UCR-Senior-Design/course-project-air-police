#https://quant-aq.github.io/py-quantaq/ library documentation
# eventually put this into a class
import quantaq
from quantaq.utils import to_dataframe
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import json
#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.
apiKey = 'AOSIIFR5L7HM6KUISW2D4UFK'


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
#return a df
def fetchData(client):

    # client = quantaq.QuantAQAPIClient(api_key = apiKey)
    #empty list for later

    #gather device infos currently limited to 10 cuz i dont wanna wait 5 years
    devices = to_dataframe(client.devices.list())

    #alternative
    #devices = fetchActiveDevices(client)
    data = []
    # get every serial number from devices
    sn = update()
    
    # #loop through each device and call data list limited to the most recent 1. 
    for i in sn:
        data.append(to_dataframe(client.data.list( sn = i, sort = "timestamp,desc", limit = 1 ) ) )
    # data = to_dataframe( client.data.list(sn = sns, sort = "timestamp,desc", limit = 1))
     

    #turns list of dataframes into 1 data fram i think.... this is the part that probably went wrong
    data = pd.concat(data, ignore_index=True)
    data = data[['sn','geo.lat', 'geo.lon','pm25', 'pm10', 'timestamp']]
    return data


#find devices that are not outputting a pm2.5 or pm10 reading


#get the client

client = quantaq.QuantAQAPIClient(api_key = apiKey)
devices = to_dataframe(client.devices.list())
print(devices.columns)
data = fetchData(client)
print(data)
# print(findNonFunctional(client))
