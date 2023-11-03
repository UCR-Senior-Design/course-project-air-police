#https://quant-aq.github.io/py-quantaq/ library documentation
# eventually put this into a class
import quantaq
from quantaq.utils import to_dataframe
import pandas as pd

#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.
apiKey = 'AOSIIFR5L7HM6KUISW2D4UFK'

#return a df
def fetchAllRecent(client):

    #empty list for later

    #gather device infos currently limited to 10 cuz i dont wanna wait 5 years
    devices = to_dataframe(client.devices.list())

    #alternative
    #devices = fetchActiveDevices(client)
    data = []
    # get every serial number from devices
    sn = ['MOD-PM-00681', 'MOD-PM-00673','MOD-PM-00682','MOD-PM-00676','MOD-PM-00665']
    
    # #loop through each device and call data list limited to the most recent 1. 
    for i in sn:
        data.append(to_dataframe(client.data.list( sn = i, sort = "timestamp,desc", limit = 1 ) ) )
    # data = to_dataframe( client.data.list(sn = sns, sort = "timestamp,desc", limit = 1))
     

    #turns list of dataframes into 1 data fram i think.... this is the part that probably went wrong
    data = pd.concat(data, ignore_index=True)
    data = data[['pm10','pm25', 'sn', 'geo.lat', 'geo.lon']]
    return data


#gather active devices
def fetchActiveDevices(client):
    devices = to_dataframe(client.devices.list(filter="device_state,eq,ACTIVE"))
    return devices

def getLongitudeLatitude(client, serialNumber):
    devices = to_dataframe(client.devices.list(limit = 10))
    # need to add a statement here in case there are some problems
    return devices.loc[devices['sn'] == serialNumber, 'geo.lat':'geo.lon']
def getAllLatitudeLongitude(client):
    devices = to_dataframe(client.devices.list())
    return devices[['sn','geo.lat', 'geo.lon']]

#get the client

client = quantaq.QuantAQAPIClient(api_key = apiKey)
who = client.whoami()
print(who)
# print to test
print(fetchAllRecent(client))
devices = to_dataframe(client.devices.list())
print(devices.columns)
# print(devices)
# print(getLongitudeLatitude(client, 'MOD-PM-00156'))
# print(  getAllLatitudeLongitude(client) )

# teams = client.teams.list()
# print(teams)

data = client.data.list( sn = "MOD-PM-00696", sort = "timestamp,desc", limit = 1 ) 
# print(data)
data = to_dataframe(data)
print(data[['pm10','pm25', 'sn']])
# print(data)