#https://quant-aq.github.io/py-quantaq/ library documentation

import quantaq
from quantaq.utils import to_dataframe
import pandas as pd

#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.
apiKey = 'AOSIIFR5L7HM6KUISW2D4UFK'

#return a df
def fetchAllRecent(client):

    #empty list for later
    data = []

    #gather device infos currently limited to 10 cuz i dont wanna wait 5 years
    devices = to_dataframe(client.devices.list(limit = 10))

    #alternative
    #devices = fetchActiveDevices(client)
    
    # get every serial number from devices
    sn = devices.loc[:,'sn']
    
    #loop through each device and call data list limited to the most recent 1. 
    for i in sn.index:
        data.append( to_dataframe(client.data.list( sn = sn[i], sort = "timestamp,asc", limit = 1 ) ) )

    #turns list of dataframes into 1 data fram i think.... this is the part that probably went wrong
    data = pd.concat(data)
    return data


#gather active devices
def fetchActiveDevices(client):
    devices = to_dataframe(client.devices.list(filter="device_state,eq,ACTIVE"))
    return devices

def getLongitudeLatitude(client, serialNumber):
    devices = to_dataframe(client.devices.list(limit = 10))
    # need to add a statement here in case there are some problems



    return devices.loc[devices['sn'] == serialNumber, 'geo.lat':'geo.lon']

#get the client
client = quantaq.QuantAQAPIClient(api_key = apiKey)
# print to test
print(fetchAllRecent(client))
print(  getLongitudeLatitude(client, 'MOD-PM-00544') )
