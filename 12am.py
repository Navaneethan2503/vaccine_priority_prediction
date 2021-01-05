from itertools import chain
import pickle
import requests

model_pkl_filename = "model.pkl"
with open(model_pkl_filename, 'rb') as file:
    model = pickle.load(file)

URL = "http://localhost:4000/api/"
MAX_PRIORITY = 3 # from 1

r = requests.get(URL + "getbooking")
if r.status_code != 200:
    raise Exception("Error")

booking = r.json()["booking"]

persons = [ [i['currentstatus'],
             i['gender']=='Male',
             i['age'],i['notimes'],
             i['workingtype'],
             i['problems']] for i in booking ]
priority = model.predict(persons)
#print(priority)

persons_priority = [[] for _ in range(MAX_PRIORITY)]
for i, p in enumerate(priority.tolist()):
    persons_priority[p-1].append(i)

confirmed = dict()
for i, j in enumerate(chain(*persons_priority)):
    #print(i, j)
    confirmed[j] = {**booking[j], **{'token': i+1}}
    confirmed[j].pop('_id', None)
    confirmed[j].pop('createdAt', None)
    confirmed[j].pop('updatedAt', None)
    confirmed[j].pop('__v', None)

#import json
#with open('test.json','w') as f:
    #json.dump({"confirmed":confirmed}, f)

r = requests.post(URL + "addconfirmed", data = {"confirmed":confirmed})
print(r.status_code, r.text)
