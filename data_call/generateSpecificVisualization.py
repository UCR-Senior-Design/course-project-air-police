import sys
import data as dc
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd



def generateVisualization(serialNumber):
    # do your generation here @Chloe and @Alex TODO
    query = """
        SELECT timestamp, pm25, pm10
        FROM Data
        WHERE sn = %s
        ORDER BY timestamp
    """
    cursor.execute(query, (serialNumber,))
    
    rows = cursor.fetchall()

    timestamps = [row[0] for row in rows]
    pm25_values = [row[1] for row in rows]
    pm10_values = [row[2] for row in rows]

    #plotting PM2.5 over time
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, pm25_values, color='blue', label='PM2.5')
    plt.xlabel('Timestamp')
    plt.ylabel('PM2.5 Value')
    plt.title('PM2.5 Trends over Time for Monitor ID: {}'.format(serialNumber))
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    #plotting PM10 over time
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, pm10_values, color='red', label='PM10')
    plt.xlabel('Timestamp')
    plt.ylabel('PM10 Value')
    plt.title('PM10 Trends over Time for Monitor ID: {}'.format(serialNumber))
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    cursor.close()
    mydb.close()
    dc.dataAnalysis()


if len(sys.argv <= 1):
    print("need a serial number")

serialNumber = sys.argv[1]
generateVisualization(serialNumber)
  #  dc.dataAnalysis()



