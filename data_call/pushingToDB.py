import data as dc

def updateDBs():
    dc.grabAllSensor()
    dc.checkOffline()
    dc.updateAllHealth()
    dc.pushDB(dc.fetchData())
    print('ok')
# updateDBs()
