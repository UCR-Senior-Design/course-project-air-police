from data_call import data as dc

# # print(dc.)
import json

fetchingData = dc.fetchData()
dc.pushDB(fetchingData)


printingNonFunctionals = dc.notFunctional()
print(printingNonFunctionals)
print(fetchingData)

dc.mapGeneration()
# dc.toJson(data)