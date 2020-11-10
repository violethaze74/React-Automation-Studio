from pymongo import MongoClient
import os
import numpy as np
import re
from time import sleep
import subprocess
import _thread
from epics import PV
from datetime import datetime

try:
    AH_DEBUG = bool(os.environ['AH_DEBUG'])
except:
    AH_DEBUG = False

pvNameList = []
alarmDict = {}


def initDatabase():
    try:
        ALARM_DATABASE = os.environ['ALARM_DATABASE']
    except:
        ALARM_DATABASE = "localhost"
    try:
        ALARM_DATABASE_REPLICA_SET_NAME = os.environ['ALARM_DATABASE_REPLICA_SET_NAME']
    except:
        ALARM_DATABASE_REPLICA_SET_NAME = "devrs"

    try:
        MONGO_ROOT_USERNAME = os.environ['MONGO_ROOT_USERNAME']
        MONGO_ROOT_PASSWORD = os.environ['MONGO_ROOT_PASSWORD']
        MONGO_ROOT_USERNAME = urllib.parse.quote_plus(
            MONGO_ROOT_USERNAME)
        MONGO_ROOT_PASSWORD = urllib.parse.quote_plus(
            MONGO_ROOT_PASSWORD)
        mongoAuth = True
    except:
        mongoAuth = False

    try:
        MONGO_INITDB_ALARM_DATABASE = os.environ['MONGO_INITDB_ALARM_DATABASE']
    except:
        MONGO_INITDB_ALARM_DATABASE = "demoAlarmDatabase"

    if (mongoAuth):
        client = MongoClient(
            'mongodb://%s:%s@%s' %
            (MONGO_ROOT_USERNAME, MONGO_ROOT_PASSWORD, ALARM_DATABASE), replicaSet=ALARM_DATABASE_REPLICA_SET_NAME)
        # Wait for MongoClient to discover the whole replica set and identify MASTER!
        sleep(0.5)
    else:
        client = MongoClient('mongodb://%s' % (ALARM_DATABASE),
                             replicaSet=ALARM_DATABASE_REPLICA_SET_NAME)
        # Wait for MongoClient to discover the whole replica set and identify MASTER!
        sleep(0.5)

    global alarmDB
    alarmDB = client[MONGO_INITDB_ALARM_DATABASE]

    # Prefix and suffix for alarmIOC pvs
    global alarmIOCPVPrefix
    global alarmIOCPVSuffix
    doc = alarmDB.config.find_one()
    try:
        alarmIOCPVPrefix = doc["alarmIOCPVPrefix"]
        alarmIOCPVSuffix = doc["alarmIOCPVSuffix"]
    except:
        if(AH_DEBUG):
            print('[Warning]', 'alarmIOCPVPrefix not instantiated')


def getListOfPVNames():
    # loop through each document = area
    for area in alarmDB.pvs.find():
        for key in area.keys():
            if (key == "pvs"):
                for pvKey in area[key].keys():
                    pvNameList.append(area[key][pvKey]["name"])
            if ("subArea" in key):
                for subAreaKey in area[key].keys():
                    if (subAreaKey == "pvs"):
                        for pvKey in area[key][subAreaKey].keys():
                            pvNameList.append(
                                area[key][subAreaKey][pvKey]["name"])


def initAlarmDict():
    for pvname in pvNameList:
        alarmName = alarmIOCPVPrefix + pvname + alarmIOCPVSuffix
        pv = PV(pvname=alarmName + "A",
                connection_timeout=0.001)
        pv.wait_for_connection(timeout=5)
        alarmDict[pvname] = pv
    # NOTIFY PV
    pv = PV(pvname=alarmIOCPVPrefix + "NOTIFY",
            connection_timeout=0.001)
    pv.wait_for_connection(timeout=5)
    alarmDict["NOTIFY"] = pv


def notifyEmail():
    pass


def notify(notifyBuffer):
    for entry in notifyBuffer:
        print(entry)


def disconnectAllPVs():
    for pvname in pvNameList:
        alarmDict[pvname].disconnect()


def clearGlobalDicts():
    global pvNameList
    del pvNameList[:]
    global alarmDict
    alarmDict.clear()


def restartNotifyServer():
    disconnectAllPVs()
    clearGlobalDicts()
    getListOfPVNames()
    initAlarmDict()
    print("Notify server restarted...")


def startNotifyServer():
    initDatabase()
    getListOfPVNames()
    initAlarmDict()

    # debug prints
    # print(alarmDict)

    print("Notify server running...")
