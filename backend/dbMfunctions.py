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