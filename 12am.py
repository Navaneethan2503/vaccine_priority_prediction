from itertools import chain
import pickle
import pymongo
import requests

model_pkl_filename = "model.pkl"
with open(model_pkl_filename, 'rb') as file:
    model = pickle.load(file)

URL = 'mongodb+srv://12am:everyday@cluster0.hqmvo.mongodb.net/'
MAX_PRIORITY = 3 # from 1

client = pymongo.MongoClient(URL)
db = client['vaccine']

booking = list(db['bookings'].find())

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

confirmed_dict = dict()
for i, j in enumerate(chain(*persons_priority)):
    #print(i, j)
    confirmed_dict[j] = {**booking[j], **{'token': i+1}}
    confirmed_dict[j].pop('createdAt', None)
    confirmed_dict[j].pop('updatedAt', None)
    confirmed_dict[j].pop('__v', None)

confirmed = [confirmed_dict[i] for i in sorted(confirmed_dict)]

db['confirmeds'].insert_many(confirmed)

## to check
#for i in db['confirmed'].find():
    #print(i)
