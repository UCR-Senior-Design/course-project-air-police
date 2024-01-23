from data_call import data as dc

# # print(dc.)
import json

fetchingData = dc.fetchData()

print("Testing DB Push")
dc.pushDB(fetchingData)

print("Adding another one")
fetchingData = dc.fetchData();
dc.pushDB(fetchingData)

print("Testing Unique Devices")
print(dc.getUniqueDevices())
print(len(dc.getUniqueDevices()))

print("Testing pullRecent()")
print(dc.getAllRecent())


print("Testing NonFunctional Again")
print(dc.notFunctional());