import requests
import datetime
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
import data as dc
from dotenv import load_dotenv
load_dotenv()
import numpy as np
import mysql.connector
from io import BytesIO
import io
import base64

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


###########################################
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
    recent = recent.rename(columns = {0: 'sn',1:'description', 2:'geo.lat', 3:'geo.lon', 4:'pmHealth',5:'sdHealth', 6:'status', 7:'Data Fraction', 9:'pm25', 10: "pm10", 11: "timestamp"})
    recent.replace(0, np.nan, inplace=True)
    return recent

"""
################aqi values
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
            aqi_values[monitor_id] = {'AQI_PM25': aqi_pm25, 'AQI_PM10': aqi_pm10}
        else:
            print(f"Missing data for monitor ID: {monitor_id}")
    return aqi_values

def print_aqi_for_all_monitors(aqi_values):
    if aqi_values:
        for monitor_id, aqi_data in aqi_values.items():
            print(f"Monitor ID: {monitor_id}")
            if aqi_data['AQI_PM25'] is not None:
                print(f"AQI_PM25")



######################PM25 and PM10 values on a graph

#apiKey = os.environ['api_key']
import data as dc
if __name__ == "__main__":
    data = dc.fetchData()
    monitor_ids = data['sn'].unique()

    for description in monitor_ids:
        monitor_data = data[data['sn'] == description]
        timestamps = pd.to_datetime(monitor_data['timestamp'])
        pm25_values = monitor_data['pm25']
        pm10_values = monitor_data['pm10']

        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, pm25_values, label='PM25', color='blue')
        plt.plot(timestamps, pm10_values, label='PM10', color='red')
        plt.title(f'PM25 and PM10 Over Time: {description}')
        plt.xlabel('Timestamp')
        plt.ylabel('Concentration')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

########################
#var con = mysql.createConnection(sqlConfig);
#    var query1 = "SELECT description FROM Devices;"
"""
def execute_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    except mysql.connector.Error as err:
        print(f"Error executing MySQL query: {err}")
        return None

def check_type(x):
    if isinstance(x, (int, float)):
        return calculate_aqi(x, 'pm25')
    else:
        print(f"Non-numeric value found: {x}")
        return None

def calculate_aqi(pm_value, pm_type):
    if pm_type == 'PM25':
        breakpoints = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5]
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500]
    elif pm_type == 'PM10':
        breakpoints = [0, 54, 154, 254, 354, 424, 504, 604]
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500]
    else:
        return None
    
    #if pm_value is None:
    #    return None
    #if pm_value is not None:
        #for i in range(len(breakpoints) - 1):
          #  if pm_value >= breakpoints[i] and pm_value <= breakpoints[i + 1]:
          #      aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i]
          #      return int(aqi)
    #else:
    #    return None
    
    if pd.isnull(pm_value):
        return None
    elif not isinstance(pm_value, (int, float)):
        return None

    description_data['AQI_PM25'] = description_data['pm25'].apply(lambda x: check_type(x))

"""
    for i in range(len(breakpoints) - 1):
        if pm_value >= breakpoints[i] and pm_value <= breakpoints[i + 1]:
            aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i]
            return int(aqi)
"""
if __name__ == "__main__":
    connection = connect()
    if connection:
        data = dc.getAllRecent()
        monitor_ids = data['sn'].unique()

        query1 = "SELECT description FROM Devices;"
        descriptions_result = execute_query(connection, query1)

        if descriptions_result:
            descriptions = [row[0] for row in descriptions_result]
            print("Descriptions from MySQL database:")
            for desc in descriptions:
                print(desc)
                description_data = data[data['description'] == desc]
                description_data['AQI_PM25'] = description_data['pm25'].apply(lambda x: calculate_aqi(x, 'PM25'))
                description_data['AQI_PM10'] = description_data['pm10'].apply(lambda x: calculate_aqi(x, 'PM10'))
                #PM25 and PM10 values over time
                plt.figure(figsize=(10, 5))
                plt.plot(description_data['timestamp'], description_data['pm25'], label='PM25')
                plt.plot(description_data['timestamp'], description_data['pm10'], label='PM10')
                plt.xlabel('Timestamp')
                plt.ylabel('Concentration (µg/m³)')
                plt.title(f'PM25 and PM10 Concentrations for {desc}')
                plt.legend()
                plt.show()
                plt.figure(figsize=(10, 5))
                plt.plot(description_data['timestamp'], description_data['AQI_PM25'], label='AQI PM25')
                plt.plot(description_data['timestamp'], description_data['AQI_PM10'], label='AQI PM10')
                plt.xlabel('Timestamp')
                plt.ylabel('AQI')
                plt.title(f'AQI Values for {desc}')
                plt.legend()
                plt.show()
                ##################
                fig = plt.figure()
                plt.plot(range(10))
                figdata = BytesIO()
                fig.savefig(figdata, format='png')
                buf = io.BytesIO()

                plt.savefig(buf, format='png')
                image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
                buf.close()

                plt.savefig(f'data_call/{}vis.png') #path is wrong but idk how to do this properly or in another way
                plt.close() 




        else:
            print("Failed to fetch descriptions from MySQL.")
