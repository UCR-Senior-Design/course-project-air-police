from data_call import data as dc

# # print(dc.)
import json

fetchingData = dc.fetchData()
printingNonFunctionals = dc.notFunctional()
print(printingNonFunctionals)
print(fetchingData)
dc.mapGeneration()
# dc.toJson(data)