from pymongo import MongoClient
import urllib.parse
import os
import json

try:
    MONGO_INITDB_ROOT_USERNAME = os.environ['MONGO_INITDB_ROOT_USERNAME']
    MONGO_INITDB_ROOT_PASSWORD = os.environ['MONGO_INITDB_ROOT_PASSWORD']
    MONGO_INITDB_ROOT_USERNAME = urllib.parse.quote_plus(
        MONGO_INITDB_ROOT_USERNAME)
    MONGO_INITDB_ROOT_PASSWORD = urllib.parse.quote_plus(
        MONGO_INITDB_ROOT_PASSWORD)
    mongoAuth = True
except:
    mongoAuth = False

MONGO_INITDB_ALARM_DATABASE = os.environ['MONGO_INITDB_ALARM_DATABASE']

try:
    DEMO_ALARMS_IOC = os.environ['DEMO_ALARMS_IOC']
    runDemoIOC = True
except:
    runDemoIOC = False

if (runDemoIOC):
    fin = open("./initDBData/pvs.json", "rt")
    data = fin.read()
    data = data.replace('$(DEMO_ALARMS_IOC)', DEMO_ALARMS_IOC)
    fin.close()
    fin = open("./initDBData/pvs.json", "wt")
    fin.write(data)
    fin.close()

if (mongoAuth):
    client = MongoClient(
        'mongodb://%s:%s@localhost' %
        (MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD))
else:
    client = MongoClient('mongodb://localhost')

dbnames = client.list_database_names()

if (MONGO_INITDB_ALARM_DATABASE not in dbnames):
    db = client[MONGO_INITDB_ALARM_DATABASE]
    print("Instantiating database:", MONGO_INITDB_ALARM_DATABASE)
    colnames = ['config', 'pvs', 'users']
    for col in colnames:
        collection = db[col]
        with open('./initDBData/' + col + '.json') as f:
            jsonData = json.load(f)
        collection.insert_many(jsonData)
    print(MONGO_INITDB_ALARM_DATABASE, "database instantiated successfully.")

    client.close()
else:
    print(MONGO_INITDB_ALARM_DATABASE,
          "databse already exists... skipping this step.")

# if (OTHER_DATABASE not in dbnames):
#     print("Instantiating database:", OTHER_DATABASE)
#     # commands
#     print(OTHER_DATABASE,"database instantiated successfully.")
# else:
#     print(OTHER_DATABASE,
#           "databse already exists... skipping this step.")


print("Mongo setup complete. Exiting mongosetup docker service. [mongodb still running!]")