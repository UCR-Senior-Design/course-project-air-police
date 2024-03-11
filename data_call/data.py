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

def pushFullDB():
    columns = ['sn','pm25','pm10', 'timestamp']
    auth = HTTPBasicAuth(apiKey,"")
    uniqueDevices = getUniqueDevices()

    for sn in uniqueDevices:
        mydb = connect()
        mycursor = mydb.cursor()
        try:
            now = datetime.now()
            today = now.strftime('%Y-%m-%d')
            reqQuery = "https://api.quant-aq.com/device-api/v1/devices/" + sn + "/data-by-date/" + today
            # print(reqQuery)
            req = requests.request("get",reqQuery, headers = None, auth = auth)
        except:
            print("Error Incorrect API Key")
            return None
        # print(req)
        jsondata = req.json()
        edata = {col: [] for col in columns}
        ##loops through all entries in djson data section
        for entry in jsondata["data"]:
            for col in columns:
                edata[col].append(entry[col])
        data = pd.DataFrame(edata).fillna(0)
        query = "INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE pm25 = VALUES(pm25), pm10= VALUES(pm10)"
        values = data.values.tolist()
        mycursor.executemany(query,values)
        mydb.commit()
        print(mycursor.rowcount, "was inserted")
        mycursor.close()
        mydb.close()
    print("Finished")

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

"""
from data import fetchData

def print_pm_values():
    data = fetchData()

    if data is not None:
        pm_data = data.loc[:, ['pm25', 'pm10']]
        print(pm_data)
    else:
        print("Failed to fetch data.")

print_pm_values()

"""
def calculate_aqi(concentration):
    if concentration is None:
        return None

    if 0 <= concentration <= 12.0:
        return linear_conversion(concentration, 0, 12, 0, 50)
    elif 12.1 <= concentration <= 35.4:
        return linear_conversion(concentration, 12.1, 35.4, 51, 100)
    elif 35.5 <= concentration <= 55.4:
        return linear_conversion(concentration, 35.5, 55.4, 101, 150)
    elif 55.5 <= concentration <= 150.4:
        return linear_conversion(concentration, 55.5, 150.4, 151, 200)
    elif 150.5 <= concentration <= 250.4:
        return linear_conversion(concentration, 150.5, 250.4, 201, 300)
    elif 250.5 <= concentration <= 350.4:
        return linear_conversion(concentration, 250.5, 350.4, 301, 400)
    elif 350.5 <= concentration <= 500.4:
        return linear_conversion(concentration, 350.5, 500.4, 401, 500)
    else:
        return None

def linear_conversion(concentration, min_concentration, max_concentration, min_aqi, max_aqi):
    return ((max_aqi - min_aqi) / (max_concentration - min_concentration)) * (concentration - min_concentration) + min_aqi

def calculate_aqi_for_all_monitors(pm25_data, pm10_data):
    aqi_values = {}
    for monitor_id in pm25_data.keys():
        pm25_value = pm25_data.get(monitor_id)
        pm10_value = pm10_data.get(monitor_id)
        if pm25_value is not None and pm10_value is not None:
            aqi_pm25 = calculate_aqi(pm25_value)
            aqi_pm10 = calculate_aqi(pm10_value)
            aqi_values[monitor_id] = {'AQI_PM2.5': aqi_pm25, 'AQI_PM10': aqi_pm10}
        else:
            print(f"Missing data for monitor ID: {monitor_id}")
    return aqi_values
pm25_data = {
    'MOD-PM-00637': 114.10195979899497, 'MOD-PM-00661': 36.25833333333333, 'MOD-PM-00673': 8.983333333333334,
    'MOD-PM-00691': 19.633333333333333, 'MOD-PM-00690': 9.1125, 'MOD-PM-00645': 19.079166666666666,
    'MOD-PM-00655': 130.61914572864322, 'MOD-PM-00692': 7.212500000000001, 'MOD-PM-00642': 11.845833333333333,
    'MOD-PM-00666': 15.279166666666667, 'MOD-PM-00682': 32.483333333333334, 'MOD-PM-00687': 11.283333333333335,
    'MOD-PM-00665': 40.733333333333334, 'MOD-PM-00678': 17.508333333333333, 'MOD-PM-00703': 5.370833333333334,
    'MOD-PM-00676': 28.833333333333336, 'MOD-PM-00639': 2.816666666666667, 'MOD-PM-00695': 6.862500000000001,
    'MOD-PM-00651': 20.062500000000004, 'MOD-PM-00677': float('nan'), 'MOD-PM-00704': 9.829166666666667,
    'MOD-PM-00688': 1.3041666666666667, 'MOD-PM-00672': 5.7125, 'MOD-PM-00709': 6.075,
    'MOD-PM-00656': 52.05781115879828, 'MOD-PM-00654': 4.9625, 'MOD-PM-00668': 4.2124999999999995,
    'MOD-PM-00659': 37.28333333333334, 'MOD-PM-00674': 60.93459227467812, 'MOD-PM-00653': 31.27916666666667,
    'MOD-PM-00641': 44.400000000000006, 'MOD-PM-00635': 9.316666666666668, 'MOD-PM-00683': 0.5333333333333334,
    'MOD-PM-00711': 19.42916666666667, 'MOD-PM-00640': 14.175, 'MOD-PM-00675': 4.545833333333333,
    'MOD-PM-00646': 51.29231759656653, 'MOD-PM-00696': 0.7583333333333334, 'MOD-PM-00652': 24.6125,
    'MOD-PM-00660': 4.375000000000001
}

pm10_data = {
    'MOD-PM-00637': 50.61443434343434, 'MOD-PM-00661': 25.336111111111112, 'MOD-PM-00673': 5.549074074074074,
    'MOD-PM-00691': 4.423148148148148, 'MOD-PM-00690': 2.025, 'MOD-PM-00645': 15.852777777777776,
    'MOD-PM-00655': 44.00833333333334, 'MOD-PM-00692': 3.713888888888889, 'MOD-PM-00642': 18.328703703703706,
    'MOD-PM-00666': 5.110185185185185, 'MOD-PM-00682': 8.624074074074073, 'MOD-PM-00687': 13.337962962962962,
    'MOD-PM-00665': 10.252777777777778, 'MOD-PM-00678': 5.8462962962962965, 'MOD-PM-00703': 1.9861111111111112,
    'MOD-PM-00676': 32.931481481481484, 'MOD-PM-00639': 14.626851851851853, 'MOD-PM-00695': 3.003703703703704,
    'MOD-PM-00651': 6.882407407407407, 'MOD-PM-00677': float('nan'), 'MOD-PM-00704': 2.55,
    'MOD-PM-00688': 0.2898148148148148, 'MOD-PM-00672': 3.222222222222
}

aqi_values = calculate_aqi_for_all_monitors(pm25_data, pm10_data)
for monitor_id, aqi_data in aqi_values.items():
    print(f"Monitor ID: {monitor_id}")
    if aqi_data['AQI_PM2.5'] is not None:
        print(f"AQI_PM2.5: {aqi_data['AQI_PM2.5']:.2f}")
    else:
        print("AQI_PM2.5: N/A")
    if aqi_data['AQI_PM10'] is not None:
        print(f"AQI_PM10: {aqi_data['AQI_PM10']:.2f}")
    else:
        print("AQI_PM10: N/A")
    print()
def print_aqi_for_all_monitors(aqi_values):
    if aqi_values:
        for monitor_id, aqi_data in aqi_values.items():
            print(f"Monitor ID: {monitor_id}")
            if aqi_data['AQI_PM2.5'] is not None:
                print(f"AQI_PM2.5: {aqi_data['AQI_PM2.5']:.2f}")
            else:
                print("AQI_PM2.5: N/A")
            if aqi_data['AQI_PM10'] is not None:
                print(f"AQI_PM10: {aqi_data['AQI_PM10']:.2f}")
            else:
                print("AQI_PM10: N/A")
            print()
    else:
        print("No AQI data available for any monitors.")

pm25_data = {
    'MOD-PM-00637': 114.10195979899497, 'MOD-PM-00661': 36.25833333333333, 'MOD-PM-00673': 8.983333333333334,
    'MOD-PM-00691': 19.633333333333333, 'MOD-PM-00690': 9.1125, 'MOD-PM-00645': 19.079166666666666,
    'MOD-PM-00655': 130.61914572864322, 'MOD-PM-00692': 7.212500000000001, 'MOD-PM-00642': 11.845833333333333,
    'MOD-PM-00666': 15.279166666666667, 'MOD-PM-00682': 32.483333333333334, 'MOD-PM-00687': 11.283333333333335,
    'MOD-PM-00665': 40.733333333333334, 'MOD-PM-00678': 17.508333333333333, 'MOD-PM-00703': 5.370833333333334,
    'MOD-PM-00676': 28.833333333333336, 'MOD-PM-00639': 2.816666666666667, 'MOD-PM-00695': 6.862500000000001,
    'MOD-PM-00651': 20.062500000000004, 'MOD-PM-00677': float('nan'), 'MOD-PM-00704': 9.829166666666667,
    'MOD-PM-00688': 1.3041666666666667, 'MOD-PM-00672': 5.7125, 'MOD-PM-00709': 6.075,
    'MOD-PM-00656': 52.05781115879828, 'MOD-PM-00654': 4.9625, 'MOD-PM-00668': 4.2124999999999995,
    'MOD-PM-00659': 37.28333333333334, 'MOD-PM-00674': 60.93459227467812, 'MOD-PM-00653': 31.27916666666667,
    'MOD-PM-00641': 44.400000000000006, 'MOD-PM-00635': 9.316666666666668, 'MOD-PM-00683': 0.5333333333333334,
    'MOD-PM-00711': 19.42916666666667, 'MOD-PM-00640': 14.175, 'MOD-PM-00675': 4.545833333333333,
    'MOD-PM-00646': 51.29231759656653, 'MOD-PM-00696': 0.7583333333333334, 'MOD-PM-00652': 24.6125,
    'MOD-PM-00660': 4.375000000000001
}

pm10_data = {
    'MOD-PM-00637': 50.61443434343434, 'MOD-PM-00661': 25.336111111111112, 'MOD-PM-00673': 5.549074074074074,
    'MOD-PM-00691': 4.423148148148148, 'MOD-PM-00690': 2.025, 'MOD-PM-00645': 15.852777777777776,
    'MOD-PM-00655': 44.00833333333334, 'MOD-PM-00692': 3.713888888888889, 'MOD-PM-00642': 18.328703703703706,
    'MOD-PM-00666': 5.110185185185185, 'MOD-PM-00682': 8.624074074074073, 'MOD-PM-00687': 13.337962962962962,
    'MOD-PM-00665': 10.252777777777778, 'MOD-PM-00678': 5.8462962962962965, 'MOD-PM-00703': 1.9861111111111112,
    'MOD-PM-00676': 32.931481481481484, 'MOD-PM-00639': 14.626851851851853, 'MOD-PM-00695': 3.003703703703704,
    'MOD-PM-00651': 6.882407407407407, 'MOD-PM-00677': float('nan'), 'MOD-PM-00704': 2.55,
    'MOD-PM-00688': 0.2898148148148148, 'MOD-PM-00672': 3.222222222222
}

aqi_values = calculate_aqi_for_all_monitors(pm25_data, pm10_data)
print_aqi_for_all_monitors(aqi_values)





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
