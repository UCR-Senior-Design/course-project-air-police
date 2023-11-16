from data_call import data as dc

# print(dc.)
import json
data = dc.fetchData()
print(data)
dc.toJson(data)