from pymongo import MongoClient
from pymongo.errors import NotMasterError
import urllib.parse
import os
import numpy as np
import re
from bson.json_util import dumps
from bson.objectid import ObjectId
from time import sleep
import subprocess
import _thread
from epics import PV, caput
from datetime import datetime

ALARM_DATABASE = os.environ['ALARM_DATABASE']
ALARM_DATABASE_REPLICA_SET_NAME = os.environ['ALARM_DATABASE_REPLICA_SET_NAME']

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

if (mongoAuth):
    client = MongoClient(
        'mongodb://%s:%s@%s' %
        (MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD, ALARM_DATABASE), replicaSet=ALARM_DATABASE_REPLICA_SET_NAME)
    # Wait for MongoClient to discover the whole replica set and identify MASTER!
    sleep(0.1)
else:
    client = MongoClient('mongodb://%s' % (ALARM_DATABASE),
                         replicaSet=ALARM_DATABASE_REPLICA_SET_NAME)
    # Wait for MongoClient to discover the whole replica set and identify MASTER!
    sleep(0.1)

pvNameList = []
areaList = []
pvDict = {}
pvInitDict = {}

pvDescDict = {}
alarmDict = {}
alarmDictInitialised = False
areaDict = {}
subAreaDict = {}

areaPVDict = {}

# Prefix and suffix for alarmIOC pvs
doc = client[MONGO_INITDB_ALARM_DATABASE].config.find_one()
alarmIOCPVPrefix = doc["alarmIOCPVPrefix"]
alarmIOCPVSuffix = doc["alarmIOCPVSuffix"]
        


def printVal(pvname=None, value=None, **kw):
    # print(pvname, value)
    pass


def propagateAreaAlarms(pvname=None, value=None, **kw):
    _thread.start_new_thread(propAreaAlarms, (
        pvname,
        value,
    ))


def propAreaAlarms(pvname, value):
    pvname = re.sub('^' + alarmIOCPVPrefix, '', pvname)
    pvname = re.sub('A$', '', pvname)
    pvname = re.sub(alarmIOCPVSuffix + '$', '', pvname)
    if (bool(areaDict)):
        # wait for areaDict to be instantiated
        areaKey = getKeys(pvname)[0]
        areaEnable, subAreaEnable, pvEnable = getEnables(pvname)

        if ("-" in areaKey):
            subArea = areaKey.split("-")[1]
            areaKey = areaKey.split("-")[0]

            enable = areaEnable and subAreaEnable and pvEnable

            if (enable):
                evaluateAreaPVs(areaKey + "-" + subArea)
                # wait for subArea to evaluate before topArea
                sleep(0.01)
                evaluateAreaPVs(areaKey)

        else:
            enable = areaEnable and pvEnable

            if (enable):
                evaluateAreaPVs(areaKey)


def evaluateAreaPVs(areaKey, fromColWatch=False):
    areaPV = areaPVDict[areaKey]
    isAlarm = False
    isAcked = False

    for key in pvDict.keys():
        if (re.sub(r"-pv\d+", "", key) == areaKey):
            # exact match of area key
            val = alarmDict[pvDict[key].pvname]["A"].value
            areaEnable, subAreaEnable, pvEnable = getEnables(
                pvDict[key].pvname)
            if (subAreaEnable != None):
                enable = areaEnable and subAreaEnable and pvEnable
            else:
                enable = areaEnable and pvEnable
            if (not enable):
                # pv not enabled
                # not alarm nor acked passed
                val = 2
            if (val == 0):
                isAlarm = True
            if (val == 1):
                isAcked = True

    if ("-" in areaKey):
        if (isAlarm):
            areaPV.value = 0
        elif (isAcked):
            areaPV.value = 1
        else:
            areaPV.value = 2
        if (fromColWatch):
            # wait for subArea to evaluate before topArea
            sleep(0.01)
            # if from col watch also reasses top area
            evaluateAreaPVs(areaKey.split("-")[0])
    else:
        # this is a top area
        evaluateTopArea(areaKey, isAlarm, isAcked)


def evaluateTopArea(topArea, isAlarm, isAcked):
    areaPV = areaPVDict[topArea]
    isAlarm = isAlarm
    isAcked = isAcked

    # print(isAlarm, isAcked)

    for area in areaList:
        if ("-" in area):
            if area.startswith(topArea):
                pv = areaPVDict[area]
                # print(pv, pv.value)
                if (pv.value == 0):
                    isAlarm = True
                if (pv.value == 1):
                    isAcked = True

    if (isAlarm):
        areaPV.value = 0
    elif (isAcked):
        areaPV.value = 1
    else:
        areaPV.value = 2


def getKeys(pvname):
    key_list = list(areaDict.keys())
    val_list = list(areaDict.values())
    areaName = key_list[val_list.index(pvname)]
    areaKey = re.sub(r"-pv\d+", "", areaName)
    pvKey = re.search(r"pv\d+", areaName).group(0)
    return areaKey, pvKey


def getEnables(pvname):
    areaKey, pvKey = getKeys(pvname)

    if ("-" in areaKey):
        subAreaKey = subAreaDict[areaKey]
        areaKey = areaKey.split("-")[0]

        doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
            {"area": areaKey})

        areaEnable = doc["enable"]
        subAreaEnable = doc[subAreaKey]["enable"]
        pvEnable = doc[subAreaKey]["pvs"][pvKey]["enable"]

    else:
        doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
            {"area": areaKey})

        areaEnable = doc["enable"]
        subAreaEnable = None
        pvEnable = doc["pvs"][pvKey]["enable"]

    return areaEnable, subAreaEnable, pvEnable


def ackPVChange(value=None, timestamp=None, **kw):
    # print("ack pv:", value)
    if value != '':
        _thread.start_new_thread(ackProcess, (
            value,
            timestamp,
        ))


def ackProcess(ackIndentifier, timestamp):
    # reset ack pv so you can ack same pv/area multiple times
    alarmDict["ACK_PV"].value = ""
    try:
        re.search(r"-pv\d+", ackIndentifier).group(0)
        isPV = True
    except:
        isPV = False

    if (isPV):
        ackAlarm(ackIndentifier, timestamp)
    else:
        # print("Area to be ACKed:",ackIndentifier)
        for key in pvDict.keys():
            if (key.startswith(ackIndentifier)):
                ackAlarm(key, timestamp)


def ackAlarm(ackIndentifier, timestamp):
    pvsev = pvDict[ackIndentifier].severity
    pvname = pvDict[ackIndentifier].pvname
    alarmPVSev = alarmDict[pvname]["A"].value

    areaKey, pvKey = getKeys(pvname)

    if (alarmPVSev == 0):
        # in alarm state - valid state for ack
        timestamp = datetime.fromtimestamp(timestamp).strftime(
            "%a, %d %b %Y at %H:%M:%S")
        # set ack time
        alarmDict[pvname]["K"].value = timestamp
        if ("-" in areaKey):
            subAreaKey = subAreaDict[areaKey]
            areaKey = areaKey.split("-")[0]
            # write to db
            client[MONGO_INITDB_ALARM_DATABASE].pvs.update_many(
                {'area': areaKey}, {
                    '$set': {
                        subAreaKey + '.pvs.' + pvKey + '.lastAlarmAckTime':
                        timestamp
                    }
                })
        else:
            # write to db
            client[MONGO_INITDB_ALARM_DATABASE].pvs.update_many(
                {'area': areaKey},
                {'$set': {
                    'pvs.' + pvKey + '.lastAlarmAckTime': timestamp
                }})

    if (pvsev > 1):
        # in alarm state still so set to acked state
        alarmDict[pvname]["A"].value = 1
    else:
        # not in alarm state so set to no alarm state
        alarmDict[pvname]["A"].value = 2


def descChange(pvname=None, value=None, host=None, **kw):
    _thread.start_new_thread(updatePVDesc, (
        pvname,
        value,
        host,
    ))


def updatePVDesc(pvname, desc, host):
    # updates description and host in waveform
    pvname = re.sub('.DESC$', '', pvname)
    pv = alarmDict[pvname]["D"]
    # status initially 39 char string for memory
    pv.put(np.array(['abcdefghijklmnopqrstuvwxyzAbcdefghijk_1', desc, host]))


def descConn(pvname=None, conn=None, **kw):
    _thread.start_new_thread(descDisconn, (
        pvname,
        conn,
    ))


def descDisconn(pvname, conn):
    if (not conn):
        pvname = re.sub('.DESC$', '', pvname)
        pv = alarmDict[pvname]["D"]
        # status initially 39 char string for memory
        pv.put(
            np.array([
                'abcdefghijklmnopqrstuvwxyzAbcdefghijk_0', "[Disconnected]",
                "[Disconnected]"
            ]))


def onChanges(pvname=None, value=None, severity=None, timestamp=None, **kw):
    global alarmDictInitialised
    if (alarmDictInitialised):
        _thread.start_new_thread(pvPrepareData, (
            pvname,
            value,
            severity,
            timestamp,
        ))
    else:
        _thread.start_new_thread(pvInitData, (
            pvname,
            value,
            severity,
            timestamp,
        ))


def pvPrepareData(pvname, value, severity, timestamp):
    timestamp = datetime.fromtimestamp(timestamp).strftime(
        "%a, %d %b %Y at %H:%M:%S")

    areaKey, pvKey = getKeys(pvname)
    areaEnable, subAreaEnable, pvEnable = getEnables(pvname)

    pvELN = []

    if ("-" in areaKey):
        subAreaKey = subAreaDict[areaKey]
        areaKey = areaKey.split("-")[0]

        doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
            {"area": areaKey})

        enable = areaEnable and subAreaEnable and pvEnable

        pvELN.append(enable)
        pvELN.append(doc[subAreaKey]["pvs"][pvKey]["latch"])
        pvELN.append(doc[subAreaKey]["pvs"][pvKey]["notify"])

    else:
        doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
            {"area": areaKey})

        enable = areaEnable and pvEnable

        pvELN.append(enable)
        pvELN.append(doc["pvs"][pvKey]["latch"])
        pvELN.append(doc["pvs"][pvKey]["notify"])

    processPVAlarm(pvname, value, severity, timestamp, pvELN)


def pvInitData(pvname, value, severity, timestamp):
    if (severity > 1):
        pvInitDict[pvname] = [value, timestamp]


def processPVAlarm(pvname, value, severity, timestamp, pvELN):
    areaKey, pvKey = getKeys(pvname)

    enable = pvELN[0]
    latch = pvELN[1]
    # notify = pvELN[2]
    newAlarm = severity > 1

    alarmCleared = not (newAlarm)
    alarmActivated = newAlarm
    alarmCurrent = alarmDict[pvname]["A"].value == 0
    alarmCurrentAcked = alarmDict[pvname]["A"].value == 1

    # alarm cleared
    if (alarmCleared and (not latch or alarmCurrentAcked or not enable)):
        # set current alarm status to NONE
        alarmDict[pvname]["A"].value = 2
    if ("-" in areaKey):
        subAreaKey = subAreaDict[areaKey]
        areaKey = areaKey.split("-")[0]
        # alarm activated and previously there wasn't
        # a latched alarm
        if (alarmActivated and not alarmCurrent):
            # set current alarm status to MAJOR
            alarmDict[pvname]["A"].value = 0
            # set alarm value
            alarmDict[pvname]["V"].value = str(value)
            # set alarm time
            alarmDict[pvname]["T"].value = timestamp
            # write to db
            client[MONGO_INITDB_ALARM_DATABASE].pvs.update_many(
                {'area': areaKey}, {
                    '$set': {
                        subAreaKey + '.pvs.' + pvKey + '.lastAlarmVal': value,
                        subAreaKey + '.pvs.' + pvKey + '.lastAlarmTime':
                        timestamp
                    }
                })
    else:
        # alarm activated and previously there wasn't
        # a latched alarm
        if (alarmActivated and not alarmCurrent):
            # set current alarm status to MAJOR
            alarmDict[pvname]["A"].value = 0
            # set alarm value
            alarmDict[pvname]["V"].value = str(value)
            # set alarm time
            alarmDict[pvname]["T"].value = timestamp
            # write to db
            client[MONGO_INITDB_ALARM_DATABASE].pvs.update_many(
                {'area': areaKey}, {
                    '$set': {
                        'pvs.' + pvKey + '.lastAlarmVal': value,
                        'pvs.' + pvKey + '.lastAlarmTime': timestamp
                    }
                })


def getListOfPVNames():
    # loop through each document = area
    for area in client[MONGO_INITDB_ALARM_DATABASE].pvs.find():
        for key in area.keys():
            if (key == "area"):
                areaList.append(area[key])
            if (key == "pvs"):
                for pvKey in area[key].keys():
                    pvNameList.append(area[key][pvKey]["name"])
            if ("subArea" in key):
                for subAreaKey in area[key].keys():
                    if (subAreaKey == "name"):
                        areaList.append(area["area"] + '-' +
                                        area[key][subAreaKey])
                    if (subAreaKey == "pvs"):
                        for pvKey in area[key][subAreaKey].keys():
                            pvNameList.append(
                                area[key][subAreaKey][pvKey]["name"])


def replaceAllInFile(filename, original, replacedWith):
    fin = open(filename, "rt")
    data = fin.read()
    data = data.replace(original, replacedWith)
    fin.close()
    fin = open(filename, "wt")
    fin.write(data)
    fin.close()


def startDemoIOC(runDemoIOC):
    if (runDemoIOC):
        replaceAllInFile("/epics/demoAlarmsIOC/db/dbDemoAlarm.db", '$(ioc)',
                         DEMO_ALARMS_IOC)
        print("Running demo alarms IOC")
        subprocess.call("./startDemoIOC.cmd", shell=True)
        print("Demo alarms IOC running successfully")

    else:
        print("Demo alarms IOC disabled")


def initSubPVDict(subArea, areaName):
    subAreaName = areaName
    for key in subArea.keys():
        if (key == "name"):
            subAreaName = subAreaName + "-" + subArea[key]
        if (key == "pvs"):
            for pvKey in subArea[key].keys():
                pvname = subArea[key][pvKey]["name"]
                pv = PV(pvname=pvname,
                        connection_timeout=0.001,
                        callback=onChanges)
                pvDict[subAreaName + "-" + pvKey] = pv
                areaDict[subAreaName + "-" +
                         pvKey] = subArea[key][pvKey]["name"]


def initPVDict():
    # loop through each document = area
    for area in client[MONGO_INITDB_ALARM_DATABASE].pvs.find():
        for key in area.keys():
            if (key == "area"):
                areaName = area[key]
            if (key == "pvs"):
                for pvKey in area[key].keys():
                    pvname = area[key][pvKey]["name"]
                    pv = PV(pvname=pvname,
                            connection_timeout=0.001,
                            callback=onChanges)
                    pvDict[areaName + "-" + pvKey] = pv
                    areaDict[areaName + "-" + pvKey] = area[key][pvKey]["name"]
            if ("subArea" in key):
                subAreaDict[areaName + "-" + area[key]["name"]] = key
                initSubPVDict(area[key], areaName)


def startAlarmIOC():
    # ALARM PVS
    lines = []
    lines.append("file \"db/Alarm.db\" {\n")
    for pvname in pvNameList:
        pvname = alarmIOCPVPrefix + pvname + alarmIOCPVSuffix
        lines.append("{ alarm_name = \"" + pvname + "\" }\n")
    lines.append("}\n")
    # remove duplicates in case multiple areas had same pv
    lines = list(dict.fromkeys(lines))
    # write to Alarms.substitutions
    alarmsSubFile = open("/epics/alarmIOC/db/Alarms.substitutions", "w")
    alarmsSubFile.writelines(lines)
    alarmsSubFile.close()
    # AREA PVS
    lines = []
    lines.append("file \"db/Area.db\" {\n")
    for area in areaList:
        pvname = alarmIOCPVPrefix + area
        lines.append("{ area_name = \"" + pvname + "\" }\n")
    lines.append("}\n")
    # remove duplicates in case multiple areas had same pv
    lines = list(dict.fromkeys(lines))
    # write to Areas.substitutions
    areasSubFile = open("/epics/alarmIOC/db/Areas.substitutions", "w")
    areasSubFile.writelines(lines)
    areasSubFile.close()
    # ACK PV
    replaceAllInFile("/epics/alarmIOC/db/Global.db", '$(ioc):',
                     alarmIOCPVPrefix)
    # run alarmIOC with newly created pvs
    print("Running alarm server IOC")
    subprocess.call("./startAlarmIOC.cmd", shell=True)
    print("Alarm server IOC running successfully")


def initialiseAlarmIOC():
    print("Intilialising alarm server IOC from database")

    for pvname in pvNameList:
        areaKey, pvKey = getKeys(pvname)
        # print(areaKey, pvKey)

        if ("-" in areaKey):
            subAreaKey = subAreaDict[areaKey]
            areaKey = areaKey.split("-")[0]

            doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
                {"area": areaKey})

            lastAlarmVal = doc[subAreaKey]["pvs"][pvKey]["lastAlarmVal"]
            lastAlarmTime = doc[subAreaKey]["pvs"][pvKey]["lastAlarmTime"]
            lastAlarmAckTime = doc[subAreaKey]["pvs"][pvKey][
                "lastAlarmAckTime"]

        else:
            doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
                {"area": areaKey})

            lastAlarmVal = doc["pvs"][pvKey]["lastAlarmVal"]
            lastAlarmTime = doc["pvs"][pvKey]["lastAlarmTime"]
            lastAlarmAckTime = doc["pvs"][pvKey]["lastAlarmAckTime"]

        pv = alarmDict[pvname]["D"]
        val = pv.get()
        # actual pv did not connect during server initialisation
        if (val.size == 0):
            # status initially 39 char string for memory
            pv.put(
                np.array([
                    'abcdefghijklmnopqrstuvwxyzAbcdefghijk_0',
                    "[Disconnected]", "[Disconnected]"
                ]))
        else:
            # if alarm was activated when server initialised
            try:
                lastAlarmVal = pvInitDict[pvname][0]
                lastAlarmTime = datetime.fromtimestamp(
                    pvInitDict[pvname][1]).strftime("%a, %d %b %Y at %H:%M:%S")
                # set current alarm status to MAJOR
                alarmDict[pvname]["A"].value = 0
            except:
                # set current alarm status to NONE
                alarmDict[pvname]["A"].value = 2

        # set alarm value
        alarmDict[pvname]["V"].value = str(lastAlarmVal)
        # set alarm time
        alarmDict[pvname]["T"].value = lastAlarmTime
        # set ack time
        alarmDict[pvname]["K"].value = lastAlarmAckTime

    global alarmDictInitialised
    alarmDictInitialised = True
    print("Alarm server IOC successfully initialised from database")


def initDescDict():
    for pvname in pvNameList:
        desc = pvname + ".DESC"
        pv = PV(pvname=desc,
                connection_timeout=0.001,
                callback=descChange,
                connection_callback=descConn)
        pvDescDict[pvname] = pv


def initAreaPVDict():
    for area in areaList:
        pvname = alarmIOCPVPrefix + area
        pv = PV(pvname=pvname, connection_timeout=0.001, callback=printVal)
        areaPVDict[area] = pv


def initAlarmDict():
    for pvname in pvNameList:
        alarmName = alarmIOCPVPrefix + pvname + alarmIOCPVSuffix
        for suff in ["", "A", "V", "T", "K"]:
            if (suff == "A"):
                pv = PV(pvname=alarmName + suff,
                        connection_timeout=0.001,
                        callback=propagateAreaAlarms)
            else:
                pv = PV(pvname=alarmName + suff,
                        connection_timeout=0.001,
                        callback=printVal)
            if (suff == ""):
                alarmDict[pvname] = {}
                alarmDict[pvname]["D"] = pv
            else:
                alarmDict[pvname][suff] = pv
    # ACK PV
    pv = PV(pvname=alarmIOCPVPrefix + "ACK_PV",
            connection_timeout=0.001,
            callback=ackPVChange)
    alarmDict["ACK_PV"] = pv


def pvCollectionWatch():
    with client[MONGO_INITDB_ALARM_DATABASE].pvs.watch() as stream:
        for change in stream:
            # print(change)
            try:
                documentKey = change["documentKey"]
                doc = client[MONGO_INITDB_ALARM_DATABASE].pvs.find_one(
                    documentKey)
                change = change["updateDescription"]["updatedFields"]
                for key in change.keys():
                    # print(key)
                    if (key == "enable"):
                        # area enable
                        topArea = doc.get("area")
                        # print(areaKey, "area enable changed!")
                        for area in areaList:
                            if ("-" in area):
                                if area.startswith(topArea):
                                    areaKey = area
                                    evaluateAreaPVs(areaKey, True)
                    elif ("pvs." in key and key.endswith(".enable")):
                        # pv enable
                        # print("enable of pv changed!")
                        pvname = None
                        keys = key.split(".")
                        for key in keys:
                            if (key != "enable"):
                                doc = doc.get(key)
                            else:
                                doc = doc.get("name")
                                pvname = doc
                        areaKey = getKeys(pvname)[0]
                        evaluateAreaPVs(areaKey, True)
                    elif (key.endswith(".enable")):
                        # subArea enable
                        areaKey = doc.get("area") + "-" + doc.get(
                            key.split(".")[0])["name"]
                        # print(areaKey, "area enable changed!")
                        evaluateAreaPVs(areaKey, True)
            except:
                print("no relevant updates")


def main():
    getListOfPVNames()
    startDemoIOC(runDemoIOC)
    startAlarmIOC()
    # Initialise string PVs for front end
    initAlarmDict()
    sleep(1.0)
    # Initialise area PVs (for alarmList)
    initAreaPVDict()
    # Initialise description PV of each alarm PV
    initDescDict()
    # Initialise alarm PVs with callback
    initPVDict()
    # Sleep to allow all connects
    sleep(1.0)
    # Initialiase saved string PVs from database
    initialiseAlarmIOC()
    # Initialise database collection watch on pvs
    # For enable change on pv to reevaluate area pvs
    _thread.start_new_thread(pvCollectionWatch, ())

    # Final debug outputs
    # print(pvDict)

    print("Alarm server running...")
    while (True):
        sleep(5.0)


main()
