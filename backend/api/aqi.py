
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
import data as dc
from dotenv import load_dotenv
load_dotenv()
import numpy as np
import io
from io import BytesIO
import base64
# import sys




def calculate_aqi(pm_value, pm_type):
    return None
    
    

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



 