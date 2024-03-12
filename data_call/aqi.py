import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os
import numpy as np
apiKey = os.environ['api_key']
def fetchData():
    ######################################################################################
    ## Inputs:                                                                          ##
    ## Output:                                                                          ##
    ##        data: dataframe of the retrieved data                                     ##
    ######################################################################################

    # apiKey
    #apiKey = os.environ['api-key']
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

if __name__ == "__main__":
    data = fetchData()
    monitor_ids = data['sn'].unique()  
    
    for monitor_id in monitor_ids:
        monitor_data = data[data['sn'] == monitor_id]
        timestamps = pd.to_datetime(monitor_data['timestamp'])
        pm25_values = monitor_data['pm25']
        pm10_values = monitor_data['pm10']
        
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, pm25_values, label='PM2.5', color='blue')
        plt.plot(timestamps, pm10_values, label='PM10', color='red')
        plt.title(f'PM2.5 and PM10 Over Time for Monitor ID: {monitor_id}')
        plt.xlabel('Timestamp')
        plt.ylabel('Concentration')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

########################
        

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

