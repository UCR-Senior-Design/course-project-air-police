import os
from dotenv import load_dotenv
load_dotenv()
import mysql.connector



def connpreDB():
    mhost = os.environ['mysqlhost']
    muer = os.environ['mysqlUser']
    mpassword = os.environ['mysqlPassword']
    mdatabase = os.environ['mysqlDB']
    mydb = mysql.connector.connect(
        host = mhost,
        user = muer,
        password = mpassword
    )
    return mydb
def conn():
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
def createDB():
    mydb = connpreDB()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE IF NOT EXISTS SaltonSea")

def dropTables():
    mydb = conn()
    sql = "DROP TABLE IF EXISTS Data"
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
    mycursor = mydb.cursor()
    sql = "DROP TABLE IF EXISTS Devices"
    mycursor.execute(sql)

def createDataTable():
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS Data (sn VARCHAR(255), pm25 DECIMAL(10,3), pm10 DECIMAL(10,3), timestamp VARCHAR(255), PRIMARY KEY(sn, timestamp))")
# createDataTable()

def createDevicesTable():
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS Devices (sn VARCHAR(255),description VARCHAR(255), lat DECIMAL(5,2), lon DECIMAL(5,2), pmHealth VARCHAR(20), sdHealth VARCHAR(20), onlne VARCHAR(10), dataFraction DECIMAL(5,4), last_seen VARCHAR(255), PRIMARY KEY(sn))")

def createUserTable():
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS User (email VARCHAR(255), username VARCHAR(30), pwd TEXT, PRIMARY KEY (username) )")

def initialize():
    createDB()
    dropTables()
    createDataTable()
    createDevicesTable()
    createUserTable()
    print("Initialized")
import data as dc
def initialFill():
    dc.grabAllSensor()
    dc.fillNAs()
    print("Filled")
initialize()
initialFill()
