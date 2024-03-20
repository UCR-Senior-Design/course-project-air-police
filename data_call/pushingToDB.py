import data as dc

def updateDBs():
    dc.grabAllSensor()
    dc.checkOffline()
    dc.updateAllHealth()
    # dc.pushDB(dc.fetchData())
    # dc.pushFullDB()
    dc.removeOldData()
    dc.fillNAs()
    print('ok')
updateDBs()
