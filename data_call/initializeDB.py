import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2 as postgre


def conn():
    # mhost = os.environ['postgrehost']
    # muer = os.environ['postgreUser']
    # mpassword = os.environ['postgrePassword']
    # mdatabase = os.environ['postgreDB']
    mydb = postgre.connect(
        os.environ['POSTGRES_URL'],
        user = os.environ['POSTGRES_USER'],
        password = os.environ['POSTGRES_PASSWORD'],
    )
    return mydb


def dropTables():
    mydb = conn()
    sql = "DROP TABLE IF EXISTS Data"
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
    mycursor = mydb.cursor()
    sql = "DROP TABLE IF EXISTS Devices"
    mycursor.execute(sql)
    mycursor.close()
    mydb.close()

def createDataTable():
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS Data (sn VARCHAR(255), pm25 DECIMAL(10,3), pm10 DECIMAL(10,3), timestamp VARCHAR(255), PRIMARY KEY(sn, timestamp))")
    mydb.commit()
    mycursor.close()
    mydb.close()
# createDataTable()

def createDevicesTable():
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS Devices (sn VARCHAR(255),description VARCHAR(255), lat DECIMAL(5,2), lon DECIMAL(5,2), pmHealth VARCHAR(20), sdHealth VARCHAR(20), onlne VARCHAR(10), dataFraction DECIMAL(5,4), last_seen VARCHAR(255), PRIMARY KEY(sn))")
    mydb.commit()
    mycursor.close()
    mydb.close()
def createUserTable():
    mydb = conn()
    mycursor = mydb.cursor()
    mycursor.execute("CREATE TABLE IF NOT EXISTS usrs (email VARCHAR(255), username VARCHAR(30), pwd TEXT, PRIMARY KEY (username) )")
    mydb.commit()
    mycursor.close()
    mydb.close()

def initialize():
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
