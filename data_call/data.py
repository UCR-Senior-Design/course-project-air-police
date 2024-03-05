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
    columns = ["sn", "id", "lat", "lon"]
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
    query = "INSERT INTO Devices (sn,id, lat, lon) VALUES (%s,%s, %s, %s) ON DUPLICATE KEY UPDATE lat = VALUES(lat), lon = VALUES(lon)"
    values = data.values.tolist()
    mycursor.executemany(query, values)
    mydb.commit()
    print(mycursor.rowcount, "was inserted")
# grabAllSensor()
def mapIdToSN(id):
    mydb = connect()
    mycursor = mydb.cursor()
    query = "SELECT d.sn FROM Devices d WHERE d.id = %s"
    values = [id]
    mycursor.execute(query, values)
    # print(mycursor.fetchone()[0])
    sn = mycursor.fetchone()
    if sn == None:
        return ""
    return sn[0]
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
    mydb = connect()
    mycursor = mydb.cursor()
    query = "SELECT Devices.*, Data.* FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn;"
    mycursor.execute(query)
    recent = mycursor.fetchall()
    recent = pd.DataFrame(recent).dropna(how='all', axis = 0).drop(columns=8, axis = 1)
    recent = recent.rename(columns = {0: 'sn',1:'id', 2:'geo.lat', 3:'geo.lon', 4:'pmHealth',5:'sdHealth', 6:'status', 7:'Data Fraction', 9:'pm25', 10: "pm10", 11: "timestamp"})
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

    # Define air quality color ranges based on PM2.5 values
    color_ranges = {
        #"Good": (0, 50),
        #"Moderate": (51, 100),
        #"Unhealthy for Sensitive Groups": (101, 150),
        #"Unhealthy": (151, 200),
        #"Very Unhealthy": (201, 300),
        #"Hazardous": (301, float('inf'))

        (0, 50): "green",
        (51, 100): "yellow",
        (101, 150): "orange",
        (151, 200): "red",
        (201, 300): "purple",
        (301, float('inf')): "maroon"
    }

    # Add markers for each monitor with appropriate air quality color
    for index, row in data.dropna(subset=['geo.lat', 'geo.lon', 'pm10']).iterrows():
        latitude = row['geo.lat']
        longitude = row['geo.lon']
        pm10_value = row['pm10']

        # Determine the air quality color based on the PM2.5 value
        marker_color = "blue"  # Default color if value doesn't fall into any range
        for (min_value, max_value), color in color_ranges.items():
            if min_value <= pm10_value <= max_value:
                marker_color = color
                break

        monitor_info = f"""
        <b>Monitor {index + 1}</b><br>
        Serial Number: {row['sn']}<br>
        Latitude: {row['geo.lat']}<br>  
        Longitude: {row['geo.lon']}<br>  
        PM2.5: {row['pm25']}<br>
        PM10: {row['pm10']}<br>
        Timestamp: {row['timestamp']}<br>
        """

        # Add marker with appropriate color
        folium.CircleMarker(
    location=[latitude, longitude],
    radius=5,
    popup=folium.Popup(html=monitor_info, max_width=300),
    color='black', 
    fill=True,
    fill_color=marker_color,  
    fill_opacity=1, 
).add_to(m)


    # Adding Legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 230px; height: 155px; 
                border:3px solid black; z-index:9999; font-size:14px;
                background-color:#f2f2f2;
                /* Custom Ornate Border */
                border-image: url('path/to/ornate-border.png') 30 round;
                ">
    &nbsp;<b>Legend</b><br>
    &nbsp;<i class="dot" style="background: green;"></i>&nbsp;Good<br>
    &nbsp;<i class="dot" style="background: yellow;"></i>&nbsp;Moderate<br>
    &nbsp;<i class="dot" style="background: orange;"></i>&nbsp;Unhealthy for Sensitive Groups<br>
    &nbsp;<i class="dot" style="background: red;"></i>&nbsp;Unhealthy<br>
    &nbsp;<i class="dot" style="background: purple;"></i>&nbsp;Very Unhealthy<br>
    &nbsp;<i class="dot" style="background: maroon;"></i>&nbsp;Hazardous<br>
    </div>
    <style>
        .dot {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
    </style>
    """

    m.get_root().html.add_child(folium.Element(legend_html))

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
