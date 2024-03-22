import dbMfunctions as dc

def updateDBs():
    dc.checkOffline()
    dc.updateAllHealth()
    dc.updateAllDataFraction()
    print('ok')
updateDBs()
