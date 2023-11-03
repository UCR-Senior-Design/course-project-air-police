#https://quant-aq.github.io/py-quantaq/ library documentation
# imports required to use the api
import quantaq
from quantaq.utils import to_dataframe
import pandas as pd

# input unique apikey here
apiKey = '7QQN18AOIHAA15UD9SNKUIA1'

# function that returns SN, particle count, and coordinates of devices passed in
def fetchSensorData(client, sn):
    data = []
    # appends raw data of each sensor in sn to a list
    for i in sn:
        data.append( to_dataframe(client.data.list( sn = i, sort="timestamp,desc", limit=1 ) ) )

    # format and return necessary data
    data = pd.concat(data)
    data = data[['sn', 'pm10','pm25', 'geo.lat', 'geo.lon']]
    return data

# driver function
def main():
    #get the client
    client = quantaq.QuantAQAPIClient(api_key = apiKey)
    who = client.whoami()
    print(who)

    # choose sensors to look at
    SN1 = "MOD-PM-00681"
    SN2 = "MOD-PM-00682"
    SN3 = "MOD-PM-00673"
    SN4 = "MOD-PM-00696"
    sn = [SN1, SN2, SN3, SN4]
           
    print (fetchSensorData(client, sn))

main()
