import pymongo
import sys
import os
import configparser
import json

import re
import random
import string

import sys
import getpass
import bcrypt
from datetime import datetime
from time import sleep

path='savedConfig/'



sys.path.insert(0,path )
#######
##configs
usePvLabelsAsDescription=False
usePvUnits=True
##########

def loadDefaultUserGroups():
    try:
        path='defaultUserGroups.json'
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        with open(path) as json_file:
            data = json.load(json_file)
            data['timestamp']=str(timestamp)
            return data
    except:
        print("Error Cant load file defaultUserGroups.json")
        return None


databaseName='adminDb'
ADMIN_DATABASE=os.getenv('ADMIN_DATABASE')
replicaSet=str(os.getenv('ADMIN_DATABASE_REPLICA_SET_NAME'))
if (ADMIN_DATABASE is None) :
    print("Enviroment variable ADMIN_DATABASE is not defined, can't intialize: ",databaseName)
else:
    print("Enviroment variable ADMIN_DATABASE: ",ADMIN_DATABASE)
    print("Enviroment variable ADMIN_DATABASE_REPLICA_SET_NAME: ",replicaSet)
    databaseURL="mongodb://"+str(ADMIN_DATABASE)
    myclient = pymongo.MongoClient(databaseURL,replicaSet=replicaSet)
    # Wait for MongoClient to discover the whole replica set and identify MASTER!
    sleep(0.1)
    dbnames = myclient.list_database_names()
    if (databaseName in dbnames):
        print("ADMIN_DATABASE already intitialized, exiting")
    else:

        mydb = myclient[databaseName]
        password='admin'
        encryptedPassword=(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))).decode('utf-8')
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        user={
            'username':'administrator',
            'password':encryptedPassword,
            'timestamp':str(timestamp)

        }
        
        usersCollection = mydb['users']

        usersCollection.insert_one(user)

        UAGS=loadDefaultUserGroups()    
        uagsCollection = mydb['UAGS']
        uagsCollection.insert_one(UAGS)
       