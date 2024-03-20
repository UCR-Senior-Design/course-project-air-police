import data as dc

def update():
    # dc.grabAllSensor()
    dc.checkOffline()
    dc.updateAllHealth()
    # dc.pushDB(dc.fetchData())
    dc.pushFullDB()
    dc.updateAllDataFraction()
    print('ok')
update()
