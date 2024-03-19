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
import io
from io import BytesIO
import base64
import sys


def check_type(x):
    if isinstance(x, (int, float)):
        return calculate_aqi(x, 'pm25')
    else:
        print(f"Non-numeric value found: {x}")
        return None

def calculate_aqi(pm_value, pm_type):

    return None
    
    if pm_type == 'PM25':
        breakpoints = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5]
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500]
    elif pm_type == 'PM10':
        breakpoints = [0, 54, 154, 254, 354, 424, 504, 604]
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500]
    else:
        return None
    
    #convert to float
    try:
        pm_value = float(pm_value)
    except ValueError:
        print(f"Error converting {pm_value} to float")
        return None
    
    #checking if pm_value is NaN
    if pd.isnull(pm_value):
        return None
    
    for i in range(len(breakpoints) - 1):
        if pm_value >= breakpoints[i] and pm_value <= breakpoints[i + 1]:
            aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i]
            return int(aqi)
    
    return None

"""
    for i in range(len(breakpoints) - 1):
        if pm_value >= breakpoints[i] and pm_value <= breakpoints[i + 1]:
            aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i]
            return int(aqi)
"""

# this will be passed into the file as an argument
# if len(sys.argv) < 2:
#     desc = "default"
# else :
#     desc = sys.argv[1:][0]
# #print(desc)


def generateAqi( desc="default" ):
    if (desc == "default" or desc == None):
        with open("public/images/refresh.png", "rb") as f:
            data = f.read()
            return base64.b64encode(data)
            
    else:

        data = dc.pullDataTime(desc, 1)
        # print(data)
        if(data.empty):
            data = dc.getAllRecent()

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
        #plt.show()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
        buf.close()
        plt.close()
        # print(image_base64)
        return image_base64



 