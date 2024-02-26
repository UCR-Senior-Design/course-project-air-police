#https://quant-aq.github.io/py-quantaq/ library documentation
# eventually put this into a class
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import requests
import base64
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta
import mysql.connector
import matplotlib.pyplot as plt

#input your apikey here... not sure if there is any safety issues of putting the api key into github, will look
## into but for now im not gonna put it in.

apiKey = os.environ['api_key']


def fetchData():
    ######################################################################################
    ## Inputs:                                                                          ##
    ## Output:                                                                          ##
    ##        data: dataframe of the retrieved data                                     ##
    ######################################################################################

    # apiKey
    columns = ['geo.lat', 'geo.lon','sn','pm25','pm10', 'timestamp']
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
    #converts dictionary to dataframe object
    data = pd.DataFrame(edata)
    return data



# database stuff cant do it in its own folder
# connect to mongoclient
def connect():
    mhost = os.environ['mysqlhost']
    muer = os.environ['mysqlUser']
    mpassword = os.environ['mysqlPassword']
    mdatabase = os.environ['mysqlDB']
    mydb = mysql.connector.connect(
        host = mhost,
        user = muer,
        password = mpassword,
        database = mdatabase
    )
    return mydb


# populates devices list
def grabAllSensor():
    auth = HTTPBasicAuth(apiKey,"")
    try:
        req = requests.request("get","https://api.quant-aq.com/device-api/v1/devices/?network_id=9", headers = None, auth = auth)
    except:
        print("Error Incorrect API Key")
        return None
    deviceListJson = req.json()
    datajson = deviceListJson['data']
    columns = ["sn", "lat", "lon" ]
    edata = {col: [] for col in columns}
    print(pd.DataFrame(datajson).keys())
    ##loops through all entries in djson data section
    for entry in datajson:
        for col in columns: 
            # since geo location is given in a list, this check is needed for our data to work properly
            if col == "lat":
                edata[col].append(entry['geo']['lat'])
            elif col == "lon":
                edata[col].append(entry['geo']['lon'])
            else:
                edata[col].append(entry[col])
    data = pd.DataFrame(edata).fillna(0)
    print(data)
    mydb = connect()
    mycursor = mydb.cursor()
    query = "INSERT INTO Devices (sn, lat, lon) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE lat = VALUES(lat), lon = VALUES(lon)"
    values = data.values.tolist()
    mycursor.executemany(query, values)
    mydb.commit()
    print(mycursor.rowcount, "was inserted")
# grabAllSensor()
def getUniqueDevices():
    #######################################################################
    ## gets all of the unique devices                                    ##
    ## PARAMETERS:                                                       ##
    ## Return:                                                           ##
    ##   list: list of unique device names                               ##
    #######################################################################

    mydb = connect()
    query = "SELECT sn FROM Devices"
    mycursor = mydb.cursor()
    mycursor.execute(query)
    results = mycursor.fetchall()
    dataframe = pd.DataFrame(results)
    list = []
    for i, sn in dataframe.iterrows():
        list.append(sn[0])
    return list


def checkOffline():
    auth = HTTPBasicAuth(apiKey,"")
    #uses requests to get data from our network
    # uses try except for error handling
    sns = getUniqueDevices()

    try:
        req = requests.request("get","https://api.quant-aq.com/device-api/v1/devices/?network_id=9" , headers = None, auth = auth)
    except:
        return None
    # print(req.json())
    list = pd.DataFrame(req.json()["data"])
    
    list = list.drop(columns={"created","url", "description", "geo"}, axis=1)
    value = []
    for index, row in list.iterrows():

        Ti = row['last_seen'].index("T")
        t = row['last_seen'][:Ti] + ' ' + row['last_seen'][Ti + 1:]
        timestamp = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        todays = datetime.today()
        #update the threshold to how many
        todays = todays - timedelta(days=1)
        ##checks if the data is outdated
        if timestamp < todays:
            temp = ["offline" ,row['sn']]
            value.append(temp)
        else:
            temp = ["online", row['sn']]
            value.append(temp)
    mydb = connect()
    # print(value)
    query = "UPDATE Devices SET onlne = %s WHERE sn = %s"
    mycursor = mydb.cursor()
    mycursor.executemany(query, value)
    mydb.commit()

def updateHealth(serialNumber):
    if serialNumber == None:
        return
    opc_flag = 2
    neph_flag = 4
    sd_flag = 8192
    # get raw data
    auth = HTTPBasicAuth(apiKey,"")
    request = "https://api.quant-aq.com/device-api/v1/devices/" + serialNumber + '/data/raw/?network_id=9'
    try:
        req = requests.request("get",request, headers = None, auth = auth)
    except:
        print("Error Incorrect API Key")
        return None
    djson = req.json()
    rawData = pd.DataFrame(djson['data'])
    curflag = rawData['flag'].iloc[0]
    opcHealthnum = (curflag & opc_flag)
    nephHealthnum = (curflag & neph_flag)
    sdhealthnum = (curflag & sd_flag)
    pmhealth = "ACTIVE"
    if opcHealthnum != 0 or nephHealthnum != 0:
        pmhealth = "ERROR"
    sdhealth = "ACTIVE"
    if sdhealthnum != 0:
        sdhealth = "ERROR"
    query = "Update Devices SET pmHealth = %s, sdHealth = %s WHERE sn = %s"
    values = [pmhealth, sdhealth, serialNumber]
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute(query, values)
    mydb.commit()




def updateAllHealth():
    sns = getUniqueDevices()
    for sn in sns:
        updateHealth(sn)

#works like a charm
# mysql portion of this is done
def pushDB(data):
    ######################################################################
    ## pushes data into the database                                    ##
    ## Parameters:                                                      ##
    ##   data: pandas dataframe from fetchData() check data.py          ##
    ## Return:                                                          ##
    ######################################################################
    # if data == None:
    #     data = fetchData()
    mydb = connect()
    mycursor = mydb.cursor()
    datas = data.fillna(0)
    datas = datas.drop('geo.lat', axis = 1)
    datas = datas.drop('geo.lon', axis = 1)
    query = "INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE pm25 = VALUES(pm25), pm10= VALUES(pm10)"
    values = datas.values.tolist()
    mycursor.executemany(query,values)
    mydb.commit()
    print(mycursor.rowcount, "was inserted")


#should  work like how pullData used to work. 
def getAllRecent():
    #########################################################################
    ## pulls Most recent data from database for each unique sn             ##
    ## PARAMETERS:                                                         ##
    ## Return:                                                             ##
    ##   data: returns a dson/ dataframe/ list / dataframe  of recent data ##
    #########################################################################
    # db, collection = connect()
    devices = getUniqueDevices()
    recent = []
    for device in devices:
        mydb = connect()
        mycursor = mydb.cursor()
        query = "SELECT * FROM Data LEFT OUTER JOIN Devices ON Data.sn = Devices.sn WHERE Data.sn = %s ORDER BY Data.timestamp"
        values = [device]
        mycursor.execute(query, values)
        recent.append(mycursor.fetchone())

    recent = pd.DataFrame(recent).dropna(how='all', axis = 0).drop(columns=4, axis=1)
    recent = recent.rename(columns = {0: 'sn', 1:'pm25', 2:'pm10', 3:'timestamp', 5:'geo.lat', 6:'geo.lon', 7:'pmHealth', 8:'sdHealh', 9: "status"})
    recent.replace(0, np.nan, inplace=True)
    return recent


#tested and works a little slow but works unless your doing a data visualization you do not need to use this.
def pullData(serialNumber=None):
    #######################################################################
    ## pulls all data from database                                      ##
    ## PARAMETERS:                                                       ##
    ## Return:                                                           ##
    ##   data: returns a dson/ dataframe/ list / dataframe  of the data  ##
    ##         of all Data historical too.                               ##
    #######################################################################
    mydb = connect()
    mycursor = mydb.cursor()
    if serialNumber == None:
        query = "SELECT * FROM Data LEFT OUTER JOIN Devices ON Data.sn = Devices.sn"
        mycursor.execute(query)
        data = mycursor.fetchall()
        data = pd.DataFrame(data).dropna(how='all', axis = 0).drop(columns=4, axis = 1)
        data = data.rename(columns = {0: 'sn', 1:'pm25', 2:'pm10', 3:'timestamp', 5:'geo.lat', 6:'geo.lon', 7:'pmHealth', 8:'sdHealh'})
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
        data = getAllRecent()
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


# this should help with some of the data visualizations.
def pullDataTime(serialNumber, time=30):
    #########################################################################
    ## pulls data from specific serialNumber within the last time days     ##
    ## PARAMETERS:                                                         ##
    ##          serialNumber: the serial number of the data needed         ##
    ##          time: how far back do you want the data to pull in (days)  ##
    ## Return:                                                             ##
    ##   data: returns a dson/ dataframe/ list / dataframe  of recent data ##
    #########################################################################
    ## check if serialNumber is None
    if(serialNumber == None):
        return pd.DataFrame()
    curDate = datetime.now()
    threshold = timedelta(days=time)
    thresh = (curDate - threshold).strftime('%Y-%m-%dT%H:%M:%S')
    query = "SELECT Data.sn, Data.pm25, Data.pm10, Data.timestamp, Devices.lat, Devices.lon FROM Data LEFT OUTER JOIN Devices ON Data.sn = Devices.sn WHERE Data.sn = %s AND  Data.timestamp > %s"
    values = [serialNumber, thresh]
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute(query, values)
    data = mycursor.fetchall()
    pdData = pd.DataFrame(data)
    return pdData





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
        data = getAllRecent()

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


        # Change the current markers to dots per Porter’s request
        folium.CircleMarker(
        location=[latitude, longitude],
        radius=1,
        popup=folium.Popup(html=monitor_info, max_width=300),
        color='blue',
        fill=True,
        fill_color='blue' 
        ).add_to(m)


    # Create a HeatMap layer based on PM2.5 values
    #heat_data = [[row['geo.lat'], row['geo.lon'], row['pm25']] for index, row in data.dropna(subset=['geo.lat', 'geo.lon', 'pm25']).iterrows()]
    #HeatMap(heat_data, radius=15).add_to(m)

    # Save the map as an HTML file
    html_file_path = 'views/map.hbs'
    m.save(html_file_path)

    # Open the HTML file in the default web browser
    webbrowser.open(html_file_path)
#####Added function to perform data analysis on the distribution of PM2.5 values#####
    
###############################################################################################################
####                                            dataAnalysis                                               ####
####            Added function to perform data analysis on the distribution of PM2.5 value                 ####
####    Will focus in the future on expanding on this data analysis to create visualizations that can be   #### 
####            consistently updated and showing the distribution over time of PM2.5 values                ####
###############################################################################################################

#def dataAnalysis():
    

    #makes plot of pm2.5 values
   # plt.figure(figsize=(10, 6))
   # plt.hist(data['pm25'].dropna(), bins=20, color='skyblue', edgecolor='black')
  #  plt.title('Distribution of PM2.5 Values')
  #  plt.xlabel('PM2.5')
  #  plt.ylabel('Frequency')
  #  plt.grid(axis='y', linestyle='--', alpha=0.7)
   # plt.show()
############################################
    ######convert data analysis PM 2.5 to html
def generate_pm25_graph():
    pm25_values = np.random.normal(20, 5, 1000)  #1000 random PM2.5 values with mean 20 and standard deviation 5
    
    #creates histogram of PM2.5 values
    plt.figure(figsize=(10, 6))
    plt.hist(pm25_values, bins=20, color='skyblue', edgecolor='black')
    plt.title('Distribution of PM2.5 Values')
    plt.xlabel('PM2.5')
    plt.ylabel('Frequency')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    temp_file_path = 'pm25_graph.png'
    plt.savefig(temp_file_path)
    
    with open(temp_file_path, 'rb') as file:
        img_data = file.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        img_html = f'<img src="data:image/png;base64,{img_base64}" alt="PM2.5 Graph">'
    
    return img_html

def dataAnalysis():
    pm25_plot_html = generate_pm25_graph()
    
    print(pm25_plot_html)





def updateDataFractionForToday(serialNumber):
    auth = HTTPBasicAuth(apiKey,"")
    #uses requests to get data from our network
    # uses try except for error handling
    query = "https://api.quant-aq.com/device-api/v1/devices/" + serialNumber + "/data-by-date/" + datetime.now().strftime('%Y-%m-%d') + "/?network_id=9"
    try:
        req = requests.request("get",query, headers = None, auth = auth)
    except:
        print("Error Incorrect API Key")
        return None
    res = req.json()
    total = res["meta"]["total"]
    fraction = total / 1440

    values = [fraction, serialNumber]
    return values

def updateAllDataFraction():
    sns = getUniqueDevices()
    list = []
    for sn in sns:
        list.append(updateDataFractionForToday(sn))
    mydb = connect()
    mycursor = mydb.cursor()
    query = "UPDATE Devices SET dataFraction = %s WHERE sn = %s"
    mycursor.executemany(query, list)
    mydb.commit()
