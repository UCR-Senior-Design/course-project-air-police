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
from pymongo import MongoClient
from pymongo import UpdateOne
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
    ##print (req)
    #loads the request into a json formatt
    djson = req.json()
    ##print (djson)

    
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


# database stuff cant do it in its own folder
# connect to mongoclient
def connect():
    connection = os.environ['c_URI']
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
    dic = data
    dic['_id'] = dic['sn']
    # print(dic)
    bu = [
        UpdateOne({"_id":doc.to_dict()["_id"]}, {"$set": doc.to_dict()},upsert=True) for i,doc in dic.iterrows()
    ]
    collection.bulk_write(bu)
    return


#tested and works a little slow but works
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
        data['geo.lat'] = data['geo'].apply(lambda x: x['lat'])
        data['geo.lon'] = data['geo'].apply(lambda x: x['lon'])
        # print(data)
        data = data.drop('geo',axis=1)
        return data
    else:
        datas = collection.find()
        data = pd.DataFrame(datas)
        # print(data)
        data['geo.lat'] = data['geo'].apply(lambda x: x['lat'])
        data['geo.lon'] = data['geo'].apply(lambda x: x['lon'])
        # print(data)
        data = data.drop('geo',axis=1)
        return data









#find devices that are not outputting a pm2.5 or pm10 reading
def notFunctional(data=None):
    ######################################################################################
    ## Inputs:                                                                          ##
    ##        data: current data to find non functional                                 ##
    ##            data must include 'sn', 'pm25', 'pm10', and 'timestamp' columns       ##
    ## Output:                                                                          ##
    ##        nf: dataframe of the list of sn, reason, and index                        ##
    ##            indicates there is a problem with the device                          ##
    ######################################################################################
    # added try
    if(data==None):
        data = pullData()
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
        if pd.isna(row['geo.lat']) or pd.isna(row['geo.lon']):
            if row['sn'] not in nonFunc:
                ind.append(index)
                reason.append('geo.lat or geo.lon not reading properly')
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

    ## Code currently works but will be fixed later. have a better version of writing to a json file. but currently do not feel like porting over.
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




import folium
import webbrowser
import pandas as pd
from folium.plugins import HeatMap


###############################################################################################################
####                                            mapGeneration                                              ####
####        Map generation function to display all currently active monitors at the time of generation,    ####
####    complete with popups that display information including the monitor number, serial number, PM2.5   #### 
####    & PM10 values, & timestamp. This is all then visualized in an HTML file generated by the function  ####
###############################################################################################################

def mapGeneration(data=None):
    if data is None:
        data = pullData()

    # Generate a map with a central location of the Salton Sea area
    central_latitude = data['geo.lat'].mean()
    central_longitude = data['geo.lon'].mean()
    m = folium.Map(location=[central_latitude, central_longitude], zoom_start=10,  tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    'contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>')

    # Add markers for each of the 46 currently active monitors to the map, each that displays a popup
    for index, row in data.dropna(subset=['geo.lat', 'geo.lon']).iterrows():
        latitude = row['geo.lat']
        longitude = row['geo.lon']
        monitor_info = f"""
    <b>Monitor {index + 1}</b><br>
    Serial Number: {row['sn']}<br>
    Latitude: {row['geo.lat']}<br>  
    Longitude: {row['geo.lon']}<br>  
    PM2.5: {row['pm25']}<br>
    PM10: {row['pm10']}<br>
    Timestamp: {row['timestamp']}<br>
        """


        # Create a custom icon with a smaller size (did this to better see the heatmap)
        icon = folium.Icon(icon='glyphicon-map-marker', color='blue', prefix='glyphicon', icon_size=(5, 5), shadow=False)

        marker = folium.Marker(location=[latitude, longitude], popup=folium.Popup(html=monitor_info, max_width=300), icon=icon)
        marker.add_to(m)

    # Create a HeatMap layer based on PM2.5 values
    heat_data = [[row['geo.lat'], row['geo.lon'], row['pm25']] for index, row in data.dropna(subset=['geo.lat', 'geo.lon', 'pm25']).iterrows()]
    HeatMap(heat_data, radius=15).add_to(m)

    # Save the map as an HTML file
    html_file_path = 'views/map.hbs'
    m.save(html_file_path)

    # Open the HTML file in the default web browser
    webbrowser.open(html_file_path)