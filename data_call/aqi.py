import requests
import datetime
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
load_dotenv()
import numpy as np
import mysql.connector

###########################################


#load_dotenv()
apiKey = os.environ['api_key']
#ik it was said not to use fetchdata here... but i cant find a way to call the database without it
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
            aqi_values[monitor_id] = {'AQI_PM2.5': aqi_pm25, 'AQI_PM10': aqi_pm10}
        else:
            print(f"Missing data for monitor ID: {monitor_id}")
    return aqi_values

def print_aqi_for_all_monitors(aqi_values):
    if aqi_values:
        for monitor_id, aqi_data in aqi_values.items():
            print(f"Monitor ID: {monitor_id}")
            if aqi_data['AQI_PM2.5'] is not None:
                print(f"AQI_PM2.5")



######################PM2.5 and PM10 values on a graph

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
        plt.plot(timestamps, pm25_values, label='PM2.5', color='blue')
        plt.plot(timestamps, pm10_values, label='PM10', color='red')
        plt.title(f'PM2.5 and PM10 Over Time: {description}')
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

def calculate_aqi(pm_value, pm_type):
    if pm_type == 'PM2.5':
        breakpoints = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5]
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500]
    elif pm_type == 'PM10':
        breakpoints = [0, 54, 154, 254, 354, 424, 504, 604]
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500]
    else:
        return None

    for i in range(len(breakpoints) - 1):
        if pm_value >= breakpoints[i] and pm_value <= breakpoints[i + 1]:
            aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i]
            return int(aqi)

if __name__ == "__main__":
    connection = connect_to_mysql()
    if connection:
        data = dc.fetchData()
        monitor_ids = data['sn'].unique()

        query1 = "SELECT description FROM Devices;"
        descriptions_result = execute_query(connection, query1)

        if descriptions_result:
            descriptions = [row[0] for row in descriptions_result]
            print("Descriptions from MySQL database:")
            for desc in descriptions:
                print(desc)
                description_data = data[data['description'] == desc]
                description_data['AQI_PM2.5'] = description_data['pm2.5'].apply(lambda x: calculate_aqi(x, 'PM2.5'))
                description_data['AQI_PM10'] = description_data['pm10'].apply(lambda x: calculate_aqi(x, 'PM10'))
                #PM2.5 and PM10 values over time
                plt.figure(figsize=(10, 5))
                plt.plot(description_data['timestamp'], description_data['pm2.5'], label='PM2.5')
                plt.plot(description_data['timestamp'], description_data['pm10'], label='PM10')
                plt.xlabel('Timestamp')
                plt.ylabel('Concentration (µg/m³)')
                plt.title(f'PM2.5 and PM10 Concentrations for {desc}')
                plt.legend()
                plt.show()
                plt.figure(figsize=(10, 5))
                plt.plot(description_data['timestamp'], description_data['AQI_PM2.5'], label='AQI PM2.5')
                plt.plot(description_data['timestamp'], description_data['AQI_PM10'], label='AQI PM10')
                plt.xlabel('Timestamp')
                plt.ylabel('AQI')
                plt.title(f'AQI Values for {desc}')
                plt.legend()
                plt.show()

        else:
            print("Failed to fetch descriptions from MySQL.")
