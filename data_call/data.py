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
import psycopg2 as postgre
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
    mydb = postgre.connect(
        os.environ['POSTGRES_URL'],
        user = os.environ['POSTGRES_USER'],
        password = os.environ['POSTGRES_PASSWORD'],
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
    columns = ["sn", "description", "lat", "lon", "last_seen"]
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
    query = "INSERT INTO Devices (sn,description, lat, lon, last_seen) VALUES (%s,%s, %s, %s, %s) ON CONFLICT (sn)  DO UPDATE SET lat = EXCLUDED.lat, lon = EXCLUDED.lon, last_seen = EXCLUDED.last_seen"
    values = data.values.tolist()
    mycursor.executemany(query, values)
    mydb.commit()
    print(mycursor.rowcount, "was inserted")
    mycursor.close()
    mydb.close()
# grabAllSensor()
# def mapIdToSN(id):
#     mydb = connect()
#     mycursor = mydb.cursor()
#     query = "SELECT d.sn FROM Devices d WHERE d.id = %s"
#     values = [id]
#     mycursor.execute(query, values)
#     # print(mycursor.fetchone()[0])
#     sn = mycursor.fetchone()
#     if sn == None:
#         return ""
#     return sn[0]
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
    mycursor.close()
    mydb.close()
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
        columns = ['sn','pm25','pm10', 'timestamp']
        edata = {col: [] for col in columns}
        ##loops through all entries in djson data section
        for entry in jsondata["data"]:
            for col in columns:
                edata[col].append(entry[col])
        data = pd.DataFrame(edata).fillna(0)
        query = "INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES (%s,%s,%s,%s) ON CONFLICT (sn,timestamp) DO UPDATE SET pm25 = EXCLUDED.pm25, pm10= EXCLUDED.pm10"
        values = data.values.tolist()
        mycursor.executemany(query,values)
        mydb.commit()
        print(mycursor.rowcount, "was inserted")
        mycursor.close()
        mydb.close()
    print("Finished")

def fillNAs():
    mydb = connect()
    mycursor = mydb.cursor()

    query = "SELECT sn, last_seen FROM Devices"
    mycursor.execute(query);
    data = pd.DataFrame(mycursor.fetchall())
    for i, d in data.iterrows():
        date = d[1][0:10]
        print(date)
        httpreq = "https://api.quant-aq.com/device-api/v1/devices/" + d[0] + "/data-by-date/" + date + "/?network_id=9"
        auth = HTTPBasicAuth(apiKey,"")
        req = requests.request("get",httpreq, headers = None, auth = auth)
        jsdata = req.json()
        columns = ['sn','pm25','pm10', 'timestamp']
        edata = {col: [] for col in columns}
        ##loops through all entries in djson data section
        for entry in jsdata["data"]:
            for col in columns:
                edata[col].append(entry[col])
        data = pd.DataFrame(edata).fillna(0)
        query = "INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES (%s,%s,%s,%s) ON CONFLICT (sn,timestamp) DO UPDATE SET pm25 = EXCLUDED.pm25, pm10= EXCLUDED.pm10"
        values = data.values.tolist()
        mycursor.close()
        mycursor = mydb.cursor()
        mycursor.executemany(query, values)
        mydb.commit()
        print(mycursor.rowcount, "was inserted")

    mycursor.close()
    mydb.close()



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
    mycursor.close()
    mydb.close()

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
    mycursor.close()
    mydb.close()




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
    query = "INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES (%s,%s,%s,%s) ON CONFLICT (sn, timestamp) DO UPDATE SET pm25 = EXCLUDED.pm25, pm10= EXCLUDED.pm10"
    values = datas.values.tolist()
    mycursor.executemany(query,values)
    mydb.commit()
    print(mycursor.rowcount, "was inserted")
    mycursor.close()
    mydb.close()


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
    query = "SELECT Devices.sn, Devices.description, Devices.lat, Devices.lon, Devices.pmHealth, Devices.sdHealth, Devices.onlne, Devices.datafraction,  Data.pm25, Data.pm10, Data.timestamp FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn;"
    mycursor.execute(query)
    recent = mycursor.fetchall()
    recent = pd.DataFrame(recent).dropna(how='all', axis = 0)
    recent = recent.rename(columns = {0: 'sn',1:'description', 2:'geo.lat', 3:'geo.lon', 4:'pmHealth',5:'sdHealth', 6:'status', 7:'Data Fraction', 8:'pm25', 9: "pm10", 10: "timestamp"})
    recent.replace(0, np.nan, inplace=True)
    mycursor.close()
    mydb.close()
    return recent


#tested and works a little slow but works unless your doing a data visualization you do not need to use this.
def pullData(desc=None):
    #######################################################################
    ## pulls all data from database                                      ##
    ## PARAMETERS:                                                       ##
    ## Return:                                                           ##
    ##   data: returns a dson/ dataframe/ list / dataframe  of the data  ##
    ##         of all Data historical too.                               ##
    #######################################################################
    mydb = connect()
    mycursor = mydb.cursor()
    if desc == None:
        query = "SELECT Devices.sn, Devices.description, Devices.lat, Devices.lon, Devices.pmHealth, Devices.sdHealth, Devices.onlne, Devices.datafraction,  Data.pm25, Data.pm10, Data.timestamp FROM Data LEFT OUTER JOIN Devices ON Data.sn = Devices.sn"
        mycursor.execute(query)
        data = mycursor.fetchall()
        data = pd.DataFrame(data).dropna(how='all', axis = 0).drop(columns=4, axis = 1)
        data = data.rename(columns = {0: 'sn',1:'description', 2:'geo.lat', 3:'geo.lon', 4:'pmHealth',5:'sdHealth', 6:'status', 7:'Data Fraction', 8:'pm25', 9: "pm10", 10: "timestamp"})
        mycursor.close()
        mydb.close()

        return data
    else:
        query = "SELECT pm25, pm10, timestamp FROM Data WHERE sn IN (SELECT sn FROM Devices WHERE description = %s ORDER BY timestamp DESC)" # LIMIT 1
        values = [desc]
        mycursor.execute(query, values)
        data = mycursor.fetchall()
        #data = pd.DataFrame(data).dropna(how='all', axis = 0).drop(columns=4, axis = 1)
        #data = data.rename(columns = {0: 'pm25',1:'pm10', 2: "timestamp"})
        mycursor.close()
        mydb.close()

        return data
    mycursor.close()
    mydb.close()


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


# monitor description is unique so it should be able to substitute for primary key sn
def pullDataTime(description, time=30):
    #########################################################################
    ## pulls data from specific serialNumber within the last time days     ##
    ## PARAMETERS:                                                         ##
    ##          serialNumber: the serial number of the data needed         ##
    ##          time: how far back do you want the data to pull in (days)  ##
    ## Return:                                                             ##
    ##   data: returns a dson/ dataframe/ list / dataframe  of recent data ##
    #########################################################################
    ## check if serialNumber is None
    if(description == None):
        return pd.DataFrame()
    curDate = datetime.now()
    threshold = timedelta(days=time)
    thresh = (curDate - threshold).strftime('%Y-%m-%dT%H:%M:%S')
    query = "SELECT Data.sn, Devices.description, Data.pm25, Data.pm10, Data.timestamp, Devices.lat, Devices.lon FROM Data LEFT OUTER JOIN Devices ON Data.sn = Devices.sn WHERE Data.sn IN (SELECT sn FROM Devices WHERE description = %s) AND Data.timestamp > %s"
    values = [description, thresh]
    mydb = connect()
    mycursor = mydb.cursor()
    mycursor.execute(query, values)
    data = mycursor.fetchall()
    pdData = pd.DataFrame(data).rename(columns = {0: 'sn', 1: 'description',2: 'pm25', 3:'pm10', 4:'timestamp', 5:'geo.lat',6:'geo.lon'})
    mycursor.close()
    mydb.close()
    #print(pdData) # uncommenting this will break generated aqi encoding!
    return pdData




import folium
import webbrowser
import pandas as pd
from folium.plugins import HeatMap
from contentful_management import Client

###############################################################################################################
####                                            mapGeneration                                              ####
####        Map generation function to display all currently active monitors at the time of generation,    ####
####    complete with popups that display information including the monitor number, serial number, PM2.5   ####
####    & PM10 values, & timestamp. This is all then visualized in an HTML file generated by the function  ####
###############################################################################################################


def mapGeneration(data=None, pm_type='pm10'):
    if data is None:
        data = getAllRecent()
    if(data.empty):
        return
    # Generate a map with a central location of the Salton Sea area
    central_latitude = data['geo.lat'].mean()
    central_longitude = data['geo.lon'].mean()
    m = folium.Map(location=[central_latitude, central_longitude], zoom_start=10,
                   tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                   attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://cartodb.com/attributions">CartoDB</a>')

    # Define air quality color ranges based on PM2.5 values
    color_ranges = {
        'pm10': {
            (0, 50): "green",
            (51, 100): "yellow",
            (101, 150): "orange",
            (151, 200): "red",
            (201, 300): "purple",
            (301, float('inf')): "maroon"
        },
        'pm25': {
            (0, 50): "green",
            (51, 100): "yellow",
            (101, 150): "orange",
            (151, 200): "red",
            (201, 300): "purple",
            (301, float('inf')): "maroon"
        }
    }

    selected_color_range = color_ranges.get(pm_type)
    # Add markers for each monitor with appropriate air quality color
    for index, row in data.dropna(subset=['geo.lat', 'geo.lon', pm_type]).iterrows():
        latitude = row['geo.lat']
        longitude = row['geo.lon']
        pm_value = row[pm_type]
        img = genTimeGraph(row['description'])
        # Determine the air quality color based on the PM2.5 value
        marker_color = "blue"  # Default color if value doesn't fall into any range
        for (min_value, max_value), color in selected_color_range.items():
            if min_value <= pm_value <= max_value:
                marker_color = color
                break



        folium.CircleMarker(
            location=[latitude, longitude],
            radius=5,
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=1,
            popup=f"""
                Serial Number: {row['sn']}<br>
                Latitude: {latitude}<br>
                Longitude: {longitude}<br>
                {pm_type.upper()}: {pm_value}<br>
                Timestamp: {row['timestamp']}<br>
                {img}
            """
        ).add_to(m)
        #border color is black now
        folium.CircleMarker(
        location=[latitude, longitude],
        radius=6,
        color="black",
        fill=False,
        ).add_to(m)


    # Adding Dropdown Menu
    dropdown_html = f"""
    <form action="/changePMType" method="post">
    <select id="pm_dropdown" name = pm_type>
        <option value="pm10" {'selected' if pm_type == 'pm10' else ''}>PM10</option>
        <option value="pm25" {'selected' if pm_type == 'pm25' else ''}>PM2.5</option>
    </select>
    <button type="submit">Change</button>
    </form>
    """

    m.get_root().html.add_child(folium.Element(dropdown_html))

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
    # html_file_path = 'views/map.hbs'
    # m.save(html_file_path)
    # print(m)
    client = Client(os.environ['ContentfulApiToken'])
    # print(type(m))
    html_content = m.get_root().render()
    entry_data = {
        'fields': {
            'testing': {
                'en-US': "hello"
            },
            'htmlContent': {
                'en-US': {
                    'nodeType': 'document',
                    'data': {},  # Add required data attribute
                    'content': [
                        {
                            'nodeType': 'paragraph',
                            'data': {},  # Add required data attribute
                            'content': [
                                {
                                    'nodeType': 'text',
                                    'value':  html_content,
                                    'data':{},
                                    'marks':[]
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }


    try:
        
            
        space_id = os.environ['ContentfulID']
        environment_id = os.environ['environmentID']
        content_type_id = 'n21o2'  # Replace 'n21o2' with the actual content type ID
        space = client.spaces().find(space_id)
        environment = space.environments().find(environment_id)
        entry_id = pm_type
        try:
            entry = client.entries(space_id, environment_id).find(entry_id)
            if(entry):
                print(entry)
                updated_entry = entry.update(entry_data)
                published_entry = updated_entry.publish()
            else:
                entry = environment.content_types().find(content_type_id).entries().create(entry_id, entry_data)
                entry.publish()
        except Exception as e:
            print('Error creating entry:', e)
            entry = environment.content_types().find(content_type_id).entries().create(entry_id, entry_data)
            entry.publish()   
            
        # environment.close()
        # space.close()
        # client.close()
        # new_entry = space.entries().create(id, entry_data)
    except Exception as e:
        print('Error creating entry:', e)
    url = f'http://localhost:3000/map?pm_type={pm_type}'
    print(url)

   # import sys
   # if len(sys.argv) > 1:
   #     mapGeneration(sys.argv[1])
   # else:
   #     mapGeneration()

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

# import glob
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
    mycursor.close()
    mydb.close()

import os
import io
from io import BytesIO
def genTimeGraph(serialNumber):
    data = pullDataTime(serialNumber, 30)
    # print(data.keys())
    plt.figure(figsize=(10, 6))
    if(data.empty):
        return

    # data = data.dropna(axis=0, how="any")
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # data.set_index('timestamp',inplace=True)
    plt.plot(data['timestamp'], data['pm25'], label = "pm2.5")
    plt.plot(data['timestamp'], data['pm10'], label = "pm10")
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("time")
    plt.ylabel("PM Values")
    plt.legend()
    # temp_file_path = 'pmtimegraph_'+serialNumber+'.png'
    # plt.savefig(temp_file_path)
    # # file_pattern = 'pmtimegraph_*.png'

    # with open(temp_file_path, 'rb') as file:
    #     img_data = file.read()
    #     img_base64 = base64.b64encode(img_data).decode('utf-8')
    #     img_html = f'<img src="data:image/png;base64,{img_base64}" alt="PM2.5 Graph"style="width:400px; height:200px;">'
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    img_html = f'<img src="data:image/png;base64,{image_base64}" alt="PM2.5 Graph"style="width:400px; height:200px;">'
    plt.clf()
    plt.close()
    # os.remove(temp_file_path)
    return img_html

def removeOldData():
    mydb = connect()
    mycursor = mydb.cursor()


    ayear = datetime.now() - timedelta(days=365)
    ayearstring = ayear.strftime('%Y-%m-%dT%H:%M:%S')

    query = "DELETE FROM Data WHERE timestamp < %s "
    values = [ayearstring]
    mycursor.execute(query, values)
    mydb.commit()
    mycursor.close()
    mydb.close()