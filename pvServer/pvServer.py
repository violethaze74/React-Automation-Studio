#!/usr/bin/env python
import gevent
from gevent import monkey; monkey.patch_all()
import time
import pymongo

import threading
import socketio
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from bson.json_util import dumps

from epics import PV
import pyads
import logging
import os
import sys
import json
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

from functools import partial
from bson.objectid import ObjectId
sys.path.insert(0, '../')
sys.path.insert(0, 'userAuthentication/')

from authenticate import  AuthoriseUser,AutheriseUserAndPermissions, AuthenticateUser
from dotenv import load_dotenv
from ctypes import memmove, addressof, c_ubyte,c_int, Structure, sizeof
from pyads.structs import SAdsNotificationHeader
import ctypes
load_dotenv()

adsSocketIO = socketio.Client();
adsSocketIO.connect('http://0.0.0.0:'+ str(os.environ['adsServerPORT']),namespaces=['/adsServer'])
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = 'gevent'
print("")
print('**************************************')
print("React Automation Studio V1.2.2")
print("")
print("pvServer Environment Variables:")
print("")
print('PYEPICS_LIBCA: '+ str(os.environ['PYEPICS_LIBCA']))
print('EPICS_BASE: '+ str(os.environ['EPICS_BASE']))
print('EPICS_CA_ADDR_LIST: '+ str(os.environ['EPICS_CA_ADDR_LIST']))
print('REACT_APP_PyEpicsServerBASEURL: '+ str(os.environ['REACT_APP_PyEpicsServerBASEURL']))
print('REACT_APP_PyEpicsServerPORT: '+ str(os.environ['REACT_APP_PyEpicsServerPORT']))
print('REACT_APP_PyEpicsServerNamespace: '+ str(os.environ['REACT_APP_PyEpicsServerNamespace']))
print('REACT_APP_EnableLogin: '+ str(os.environ['REACT_APP_EnableLogin']))

#pyads.open_port()
#remote_ip = str(os.environ['ADS_SERVER'])
#print("ads_remote_ip",remote_ip)
#ads_adr = pyads.AmsAddr('127.0.0.1.1.1', pyads.PORT_SPS1)
#pyads.add_route(ads_adr, remote_ip)

#app = Flask(__name__, static_folder="../build/static", template_folder="../build")
app = Flask(__name__)
#@app.route('/', defaults={'path': ''})
#@app.route('/<path:path>')
#def index(path):

#    return render_template('index.html', async_mode=socketio.async_mode)




REACT_APP_DisableLogin=not(os.getenv('REACT_APP_EnableLogin')=='true')
if (REACT_APP_DisableLogin) :
    print("Authenitcation and Authorisation is DISABLED")
else:
    print("Authenitcation and Authorisation is ENABLED")
print("")

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = threading.Lock()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



clientPVlist={};
clientDbWatchList={};
clientAdsPlcList={};

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0

def check_pv_initialized_after_disconnect():


    global clientPVlist,clientAdsPlcList
    while (True):
       for pvname in clientPVlist :
          if (clientPVlist[pvname]['initialized']==False):
              if (clientPVlist[pvname]['isConnected']):
                  if ('pva://' in pvname):
                      clientPVlist[pvname]['pv'].get(as_string=True)
                      d=clientPVlist[pvname]['pv'].get_with_metadata(with_ctrlvars=True,use_monitor=True)
                      if  (clientPVlist[pvname]['pv'].value)!=None :
                          for keys in d:
                              if(str(d[keys])=='nan'):
                                  d[keys]=None

                          if(clientPVlist[pvname]['pv'].count >1):
                              d['value']=list(d['value'])
                          if(clientPVlist[pvname]['pv'].count ==0):  #work around for unitilized float array
                              if ('epics.dbr.c_float_Array_0' in str(type(d['value']))):
                                  print("type is epics.dbr.c_float_Array_0")
                                  d['value']=[]
                          d['pvname']= pvname
                          d['newmetadata']= 'True'
                          d['connected']= '1'
                          d['emitter']="request_pv_info: pv not in list"
                          d['chid']=str(d['chid'])
                          try:
                              rw_room=str(pvname)+'rw'
                              socketio.emit(pvname,d,room=rw_room,namespace='/pvServer')
                              d['write_access']=False
                              ro_room=str(pvname)+'ro'
                              socketio.emit(pvname,d,room=ro_room,namespace='/pvServer')
                              clientPVlist[pvname]['isConnected']=True
                              clientPVlist[pvname]['initialized']=True
                          #
                          except TypeError:
                            #"A type error exists in metadata dictionary and can't be converted into JSON format, previously this was caused by in CHID of type c_long(), a work arround exits, if CHID is not a c_long then try debugging")
                              print("***EPICS PV info initial request info error: ")
                              print("PV name: "+ str(pvname))
                              print("PyEpics PV metadata: "+ str(d))
                              print("A type error exists in metadata dictionary and can't be converted into JSON format, previously this was caused by in CHID of type c_long(), a work arround exits, if CHID is not a c_long then try debugging")
                              clientPVlist[pvname]['isConnected']=True
                              clientPVlist[pvname]['initialized']=False
                              print(type(d['value']))
                              if ('epics.dbr.c_float_Array_0' in str(type(d['value']))):
                                  print("type is epics.dbr.c_float_Array_0")
                              d={}
                              d['pvname']= pvname
                              d['connected']= '0'

                              socketio.emit(pvname,d,room=str(pvname),namespace='/pvServer')
                          except:
                              print("Unexpected error:", sys.exc_info()[0])
                              raise
                  elif ('ads://' in pvname):
                      print("check_pv_initialized_after_disconnect:",pvname)
       # for plcName in clientAdsPlcList :
       #     if not 'plc' in clientAdsPlcList[plcName]:
       #         print("check_pv_initialized_after_disconnect: No PLC object:",plcName)
       #
       #     else:
       #         if clientAdsPlcList[plcName]['state']=='opened':
       #             #isOpen=clientAdsPlcList[plcName]['plc'].is_open;
       #             #print(plcName," is open: ",isOpen)
       #             try:
       #                 state=clientAdsPlcList[plcName]['plc'].read_state();
       #                 print("plc state",state)
       #                 clientAdsPlcList[plcName]['state']='running'
       #
       #
       #
       #             except:
       #                 clientAdsPlcList[plcName]['state']=='readStateError'
       #         elif clientAdsPlcList[plcName]['state']=='running':
       #              #isOpen=clientAdsPlcList[plcName]['plc'].is_open;
       #              #print(plcName," is open: ",isOpen)
       #             try:
       #                 state=clientAdsPlcList[plcName]['plc'].read_state();
       #                 print(plcName,clientAdsPlcList[plcName]['state'],"plc state",state)
       #                 clientAdsPlcList[plcName]['state']='running'
       #
       #
       #
       #             except:
       #                 clientAdsPlcList[plcName]['state']='readStateError'
       #                 print(plcName,clientAdsPlcList[plcName]['state'],"plc next state",'readStateError')
       #                 try:
       #                      print("delete_route: ",clientAdsPlcList[plcName]['PlcAmsID'] )
       #                      clientAdsPlcList[plcName]['plc'].delete_route(clientAdsPlcList[plcName]['PlcAmsID']);
       #                      for handles in clientAdsPlcList[plcName]['plc']['notificationHandles']:
       #                          clientAdsPlcList[plcName]['plc'].del_device_notification(*handle)
       #                      clientAdsPlcList[plcName]['plc'].close_port();
       #                      clientAdsPlcList[plcName]['plc'].close();
       #
       #                 except:
       #                      print("123123closing previous connection failed:",plcName)
       #
       #
       #
       #
       #
       #         elif clientAdsPlcList[plcName]['state']=='readStateError':
       #             print(plcName,clientAdsPlcList[plcName]['state'])
       #             plcPinAlive=ping(clientAdsPlcList[plcName]['PlcIP'])
       #             if plcPinAlive:
       #                 print("ping: ",plcName," is alive")
       #                 clientAdsPlcList[plcName]['state']='pingedAlive'
       #
       #         elif clientAdsPlcList[plcName]['state']=='pingedAlive':
       #             print("closing previous connection to:",plcName)
       #             try:
       #                 #clientAdsPlcList[plcName]['plc'].close();
       #                 clientAdsPlcList[plcName]['state']='closed'
       #             except:
       #                 print("closing previous connection failed:",plcName)
       #                 clientAdsPlcList[plcName]['state']='reconnect'
       #
       #         elif clientAdsPlcList[plcName]['state']=='closed':
       #             #print("closed, but checking is_open:",plcName,clientAdsPlcList[plcName]['plc'].is_open)
       #             clientAdsPlcList[plcName]['state']='reconnect'
       #             clientAdsPlcList[plcName]['plc']=None;
       #         elif clientAdsPlcList[plcName]['state']=='reconnect':
       #             #importlib.reload(pyads)
       #             print("PCL pinged alive attempting to establish an ads connection:",plcName)
       #             pyads.open_port();
       #             pyads.add_route_to_plc(clientAdsPlcList[plcName]['hostAmsID'], clientAdsPlcList[plcName]['hostIp'], clientAdsPlcList[plcName]['PlcIP'], clientAdsPlcList[plcName]['username'], clientAdsPlcList[plcName]['password'], route_name=clientAdsPlcList[plcName]['hostIp'],added_net_id=clientAdsPlcList[plcName]['hostAmsID'])
       #             clientAdsPlcList[plcName]['routeAdded']=True;
       #             clientAdsPlcList[plcName]['connectionAdded']=True;
       #             plc = pyads.Connection(clientAdsPlcList[plcName]['PlcAmsID'], 851, clientAdsPlcList[plcName]['PlcIP'])
       #             plc.set_timeout(5000)
       #
       #             clientAdsPlcList[plcName]['plc']=plc;
       #             clientAdsPlcList[plcName]['connectionAdded']=True;
       #
       #             clientAdsPlcList[plcName]['plc'].open()
       #             clientAdsPlcList[plcName]['state']='opened';
       #             clientAdsPlcList[plcName]['plcOpened']=True;


                   #
                   # print('########## \n\r',plcName,)
                   # print('readStateError',clientAdsPlcList[plcName]['readStateError'])
                   # print('isDisconnected',clientAdsPlcList[plcName]['isDisconnected'])
                   # print('isOpen',clientAdsPlcList[plcName]['plc'].is_open)
                   # print('isConnected',clientAdsPlcList[plcName]['isConnected'])
                   # print('isDisconnected',clientAdsPlcList[plcName]['isDisconnected'])
                   # print('routeAdded',clientAdsPlcList[plcName]['routeAdded'])
                   # print('connectionAdded',clientAdsPlcList[plcName]['connectionAdded'])
                   # print('plcOpened',clientAdsPlcList[plcName]['plcOpened'])


               #if not isOpen:
                #   print("check_pv_initialized_after_disconnect: plc not open")

       time.sleep(0.1)



def onValueChanges(pvname=None,count=None,char_value=None,severity=None,status=None, value=None, timestamp=None, **kw):
    global clientPVList
    pvname1='pva://'+str(pvname)
    if(clientPVlist[pvname1]['initialized']==True):
        if (float(count)== 1):
           socketio.emit(pvname1,
              {'pvname': pvname1,'newmetadata': 'False','value': str(value),'char_value': str(char_value),'count':count, 'connected':'1', 'severity': severity,'timestamp':timestamp
              },room='pva://'+str(pvname),namespace='/pvServer')
        else:
           d={'pvname': pvname1,'newmetadata': 'False','value': list((value)),'count':count, 'connected':'1', 'severity': severity,'timestamp':timestamp}
           socketio.emit(pvname1,d,room='pva://'+str(pvname),namespace='/pvServer')


def onConnectionChange(pvname=None, conn= None, value=None, **kws):
    global clientPVlist
    pvname1='pva://'+str(pvname)

    if (conn==True):
        try:
            clientPVlist[pvname1]['isConnected']=True
            clientPVlist[pvname1]['initialized']=False

        except:
           error=1



    else:

        d={}
        d['pvname']= pvname
        d['connected']= '0'
        d['emitter']="onConnectionChange: disconnected"
        try:
            clientPVlist[pvname1]['isConnected']=False
            clientPVlist[pvname1]['initialized']=False
            socketio.emit(pvname1,d,room=str(pvname1),namespace='/pvServer')
        except:
            error=2



def background_thread():

    count = 0
    threading.Thread(target=check_pv_initialized_after_disconnect).start()

    while True:
        socketio.sleep(0.1)





@socketio.on('write_to_pv', namespace='/pvServer')
def test_write(message):
    global clientPVlist,thread_lock2,REACT_APP_DisableLogin
    #print("Test")
    authenticated=False
    if REACT_APP_DisableLogin:

        accessControl={'userAuthorised':True,'permissions':{'read':True,'write':True}}
    else :
        accessControl=AutheriseUserAndPermissions(message['clientAuthorisation'],message['pvname'])
        authenticated=accessControl['userAuthorised']

    if accessControl['userAuthorised']:
        if accessControl['permissions']['write']:
            pvname1= str(message['pvname'])
            if "pva://" in pvname1:
                pvname2=pvname1.replace("pva://","")
                try:
                    clientPVlist[pvname1]['pv'].put(message['data']);
                except:
                    print("***EPICS PV put error: ")
                    print("PV name: "+ str(pvname2))
                    print("Value to put : "+str(message['data']))
            elif "ads://" in pvname1:
                try:
                    print("writing to ads",message)
                    adsSocketIO.emit('write_by_name',message,namespace='/adsServer')

                except:
                    print("***ADS write_by_name error: ")
                    print("Name: "+ str(pvname1))
                    print("Value to write : "+str(message['data']))





            else: print("Unknown PV type")
        else:
            print("***PV put error: write access denied ")
            print("PV name: "+ str(message['pvname']))
            print("Value to put : "+str(message['data']))
    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')






def AdsCallback(notification,name,pvname,datatype):
        #print("AdsCallback")
        #print("################callback")
        #print("pvname",pvname)
        #print("notification",notification)
        #print("name",name)

        contents = notification.contents
        #print("contents",contents)
        #print("contents.data",contents.data)
        #print("contents.cbSampleSize",contents.cbSampleSize)
        #print("contents.nTimestamp",contents.nTimeStamp)
        epoch_diff = 116444736000000000;
        rate_diff = 10000000;
        timestamp=(contents.nTimeStamp-epoch_diff)/rate_diff
        #print(timestamp)

        data_size = contents.cbSampleSize
        data = (c_ubyte * data_size).from_address(addressof(contents) + SAdsNotificationHeader.data.offset)
        #print("data",data)
        value = bytearray(data)
        #print("value",value[0],value[1] )
        if datatype in ["BOOL","INT"]:
            x=int.from_bytes(value, byteorder='little', signed=True)
            socketio.emit(pvname,
               {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':'1', 'severity': 0,'timestamp':timestamp
               },room=pvname,namespace='/pvServer')
        elif datatype in ["LINT"]:
            print("data_size",data_size)
            x=int.from_bytes(value, byteorder='little', signed=True)
            socketio.emit(pvname,
               {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':'1', 'severity': 0,'timestamp':timestamp
               },room=pvname,namespace='/pvServer')

        else:
            print("undeifned callback datatype:",datatype)
        #print('x',x)
        #var = list(map(int, bytearray(contents.data)[0:contents.cbSampleSize]))
        #print("var",var)
        #ba=bytearray(contents.data)[0:contents.cbSampleSize]
        #print("ba",ba)
        #print("str(ba[0],str(ba[1]))",str(ba[0]),str(ba[1]))


    #    var = map(bool, bytearray(contents.data)[0:contents.cbSampleSize])[0]
    #    print("var",var)

###########


@adsSocketIO.on('adsData', namespace='/adsServer')
def adsData(message):
    #print("adsData",str(message))
    message['write_access']=True
    socketio.emit(message['pvname'],
      message,room=message['pvname'],namespace='/pvServer')


@socketio.on('request_pv_info', namespace='/pvServer')
def test_message(message):
    global clientPVlist,REACT_APP_DisableLogin,clientAdsPlcList,adsSocketIO
    pvname1= str(message['data'])
    authenticated=False
    if REACT_APP_DisableLogin:
        authenticated=True
        accessControl={'userAuthorised':True,'permissions':{'read':True,'write':True}}
    else :
        accessControl=AutheriseUserAndPermissions(message['clientAuthorisation'],pvname1)
        authenticated=accessControl['userAuthorised']

    if accessControl['userAuthorised'] :


        if not (pvname1 in	clientPVlist):

            if "pva://" in pvname1:


                if(accessControl['permissions']['read']):
                    if(accessControl['permissions']['write']):
                        join_room(str(pvname1)+'rw')
                        join_room(str(pvname1))
                    else:
                        join_room(str(pvname1)+'ro')
                        join_room(str(pvname1))
                    pvname2=pvname1.replace("pva://","")
                    pv= PV(pvname2,connection_timeout=0.002,connection_callback= onConnectionChange)
                    pvlist={}
                    pvlist['pv']=pv
                    pvlist['isConnected']=False
                    pvlist['initialized']=False
                    clientPVlist[pvname1]=pvlist
                    clientPVlist[pvname1]['pv'].add_callback(onValueChanges,index=0)
            elif "ads://" in pvname1:

                print("ads request 0")
                print("ads pvname1",pvname1)
                if(accessControl['permissions']['read']):
                    if(accessControl['permissions']['write']):
                        join_room(str(pvname1)+'rw')
                        join_room(str(pvname1))
                    else:
                        join_room(str(pvname1)+'ro')
                        join_room(str(pvname1))
                    str1=pvname1.replace("ads://","")
                    strings=  str1.split(':')
                    #print(strings)
                    try:
                        adsSocketIO.emit('request_pv_info',message,namespace='/adsServer')
                    except:
                        print("cant emit to adsServer",message)


            else:
                print("Unknown PV type")


        else:

            if "pva://" in pvname1:
                if(accessControl['permissions']['read']):
                    if(accessControl['permissions']['write']):
                        join_room(str(pvname1)+'rw')
                        join_room(str(pvname1))
                    else:
                        join_room(str(pvname1)+'ro')
                        join_room(str(pvname1))
                    pvname2=pvname1.replace("pva://","")
                    clientPVlist[pvname1]['initialized']=False


            else: print("Unknown PV type")
    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')

@socketio.on('databaseRead', namespace='/pvServer')
def databaseRead(message):
    global clientPVlist,REACT_APP_DisableLogin
    dbURL= str(message['dbURL'])

    #print("databaseRead: SSID: ",request.sid,' dbURL: ', dbURL)
    #print("message:",str(message))
    authenticated=False
    if REACT_APP_DisableLogin:
        authenticated=True
        accessControl={'userAuthorised':True,'permissions':{'read':True,'write':True}}
    else :
        accessControl=AutheriseUserAndPermissions(message['clientAuthorisation'],dbURL)
        authenticated=accessControl['userAuthorised']

    if accessControl['userAuthorised'] :
        if "mongodb://" in dbURL:

            #print("mongodb database connection request: ",dbURL)
            str1=dbURL.replace("mongodb://","")
            strings=  str1.split(':')
            try:
                Parametersstr=str1.split("Parameters:")[1]
                parameters=json.loads(Parametersstr)
            except:
                raise Exception("Parameters are not defined")

            #print("Parameters:",str(parameters))
            if(len(strings)>=3):
                database= strings[0];
                dbName=   strings[1];
                colName=  strings[2];
                #print("database: ", database, "length: ", len(database))
                #print("dbName: "  ,   dbName, "length: ", len(dbName))
                #print("colName: " ,  colName, "length: ", len(colName))
                ### must insert a better error detection here

                if ((len(database)>0) and (len(dbName)>0) and (len(colName)>0)):
                    write_access=False
                    if(accessControl['permissions']['read']):
                        if(accessControl['permissions']['write']):
                            join_room(str(dbURL)+'rw')
                            write_access=True
                            #join_room(str(dbURL))
                        else:
                            join_room(str(dbURL)+'ro')
                            write_access=False
                            #join_room(str(dbURL))
                        try:
                            print("connecting: "+dbURL)
                            try:
                                myclient = pymongo.MongoClient("mongodb://"+ str(os.environ[database])+"/",serverSelectionTimeoutMS=10)
                                myclient.server_info()
                            except pymongo.errors.ServerSelectionTimeoutError as err:
                                print(err)
                                return "Ack: Could not connect to MongoDB: "+str(dbURL)


                            mydb = myclient[dbName]

                            mycol=mydb[colName]
                            try:
                                query=parameters['query']
                #                print("using query:",query)
                                X=mycol.find(query)
                            except:
                                X=mycol.find()


                            #for x in X:
                                #print(x)
                            print("done: "+dbURL)


                            data=dumps(X)
                            d={'dbURL': dbURL,'write_access':write_access,'data': data}

                            eventName='databaseData:'+dbURL;
                #            print("eventName",eventName)
                            socketio.emit(eventName,d,request.sid,namespace='/pvServer')
                            return "OK"
                        except:
                            print("could not connect to MongoDB: ",dbURL)
                            return "Ack: Could not connect to MongoDB: "+str(dbURL)
                else:
                    print("Malformed database URL, must be in format: mongodb://databaseID:database:collection")
            else:
                print("Malformed database URL, must be in format: mongodb://databaseID:database:collection")





        else:
            print("Unknown PV type")
    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')

@socketio.on('databaseBroadcastRead', namespace='/pvServer')
def databaseBroadcastRead(message):
    global clientPVlist,REACT_APP_DisableLogin
    dbURL= str(message['dbURL'])

    #print("databaseRead: SSID: ",request.sid,' dbURL: ', dbURL)
    #print("message:",str(message))
    authenticated=False
    if REACT_APP_DisableLogin:
        authenticated=True
        accessControl={'userAuthorised':True,'permissions':{'read':True,'write':True}}
    else :
        accessControl=AutheriseUserAndPermissions(message['clientAuthorisation'],dbURL)
        authenticated=accessControl['userAuthorised']

    if accessControl['userAuthorised'] :
        if "mongodb://" in dbURL:

    #        print("mongodb database connection request: ",dbURL)
            str1=dbURL.replace("mongodb://","")
            strings=  str1.split(':')
            try:
                Parametersstr=str1.split("Parameters:")[1]
                parameters=json.loads(Parametersstr)
            except:
                raise Exception("Parameters are not defined")

    #        print("Parameters:",str(parameters))
            if(len(strings)>=3):
                database= strings[0];
                dbName=   strings[1];
                colName=  strings[2];
    #            print("database: ", database, "length: ", len(database))
    #            print("dbName: "  ,   dbName, "length: ", len(dbName))
    #            print("colName: " ,  colName, "length: ", len(colName))
                ### must insert a better error detection here

                if ((len(database)>0) and (len(dbName)>0) and (len(colName)>0)):
                    write_access=False
                    if(accessControl['permissions']['read']):
                        if(accessControl['permissions']['write']):
                            join_room(str(dbURL)+'rw')
                            write_access=True
                            #join_room(str(dbURL))
                        else:
                            join_room(str(dbURL)+'ro')
                            write_access=False
                            #join_room(str(dbURL))
                        try:
    #                        print("connecting: "+dbURL)
                            try:
                                myclient = pymongo.MongoClient("mongodb://"+ str(os.environ[database])+"/",serverSelectionTimeoutMS=10)
                                myclient.server_info()
                            except pymongo.errors.ServerSelectionTimeoutError as err:
                                print(err)
                                return "Ack: Could not connect to MongoDB: "+str(dbURL)

                            mydb = myclient[dbName]

                            mycol=mydb[colName]
                            try:
                                query=parameters['query']
                    #            print("using query:",query)
                                X=mycol.find(query)
                            except:
                                X=mycol.find()


                            #for x in X:
                                #print(x)
    #                        print("done: "+dbURL)


                            data=dumps(X)


                            eventName='databaseData:'+dbURL;
    #                        print("eventName",eventName)
                            d={'dbURL': dbURL,'write_access':write_access,'data': data}
                            socketio.emit(eventName,d,str(dbURL)+'rw',namespace='/pvServer')
                            d={'dbURL': dbURL,'write_access':False,'data': data}
                            socketio.emit(eventName,d,str(dbURL)+'ro',namespace='/pvServer')
                            return 'OK'
                        except:
                            print("could not connect to MongoDB: ",dbURL)
                            return "Ack: Could not connect to MongoDB: "+str(dbURL)
                else:
                    print("Malformed database URL, must be in format: mongodb://databaseID:database:collection")
            else:
                print("Malformed database URL, must be in format: mongodb://databaseID:database:collection")





        else:
            print("Unknown PV type")
    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')


@socketio.on('databaseUpdateOne', namespace='/pvServer')
def databaseUpdateOne(message):
    global clientPVlist,REACT_APP_DisableLogin
    dbURL= str(message['dbURL'])

#    print("databaseUpdate: SSID: ",request.sid,' dbURL: ', dbURL)
#    print("message:",str(message))
    authenticated=False
    if REACT_APP_DisableLogin:
        authenticated=True
        accessControl={'userAuthorised':True,'permissions':{'read':True,'write':True}}
    else :
        accessControl=AutheriseUserAndPermissions(message['clientAuthorisation'],dbURL)
        authenticated=accessControl['userAuthorised']

    if accessControl['userAuthorised'] :
        if accessControl['permissions']['write']:
            if "mongodb://" in dbURL:

#                print("mongodb database connection request: ",dbURL)
                str1=dbURL.replace("mongodb://","")
                strings=  str1.split(':')
                if(len(strings)==3):
                    database= strings[0];
                    dbName=   strings[1];
                    colName=  strings[2];
#                    print("database: ", database, "length: ", len(database))
#                    print("dbName: "  ,   dbName, "length: ", len(dbName))
#                    print("colName: " ,  colName, "length: ", len(colName))
                    ### must insert a better error detection here

                    if ((len(database)>0) and (len(dbName)>0) and (len(colName)>0)):


                        try:
                            print("connecting: "+dbURL)
                            try:
                                myclient = pymongo.MongoClient("mongodb://"+ str(os.environ[database])+"/")
                                myclient.server_info()
                            except pymongo.errors.ServerSelectionTimeoutError as err:
                                print(err)
                                return "Ack: Could not connect to MongoDB: "+str(dbURL)

                            mydb = myclient[dbName]

                            mycol=mydb[colName]
                            id=message['id']
                            newvalues=message['newvalues']
                            try:
#                                print("add newvalues")
#                                print("dbName:",dbName)
#                                print("colName:",colName)
#                                print("id:",str(id))
#                                print("newvalues message:",str(newvalues))
                                mydb[colName].update_one({'_id':ObjectId(str(id))},newvalues)

                            except Exception as e: print(e)



#                            print("done: "+dbURL)

                            try:
                                responseID=message['responseID']
                            except:
                                responseID="";

                            #eventName='databaseUpdateOne';
    #                        print("eventName",eventName)
                            return 'OK'
                        except:
                            print("could not connect to MongoDB: ",dbURL)
                            return "Ack: Could not connect to MongoDB: "+str(dbURL)

                else:
                    print("Malformed database URL, must be in format: mongodb://databaseID:database:collection")
            else:
                print("Unknown db type type: ",dbURL)
        else:
            print("write access denied to database URL: ", dbURL)

    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')


@socketio.on('databaseInsertOne', namespace='/pvServer')
def databaseInsertOne(message):
    global clientPVlist,REACT_APP_DisableLogin
#    print("databaseInsertOne")
    dbURL= str(message['dbURL'])

#    print("databaseInsertOne: SSID: ",request.sid,' dbURL: ', dbURL)
#    print("message:",str(message))
    authenticated=False
    if REACT_APP_DisableLogin:
        authenticated=True
        accessControl={'userAuthorised':True,'permissions':{'read':True,'write':True}}
    else :
        accessControl=AutheriseUserAndPermissions(message['clientAuthorisation'],dbURL)
        authenticated=accessControl['userAuthorised']

    if accessControl['userAuthorised'] :
        if accessControl['permissions']['write']:
            if "mongodb://" in dbURL:

#                print("mongodb database connection request: ",dbURL)
                str1=dbURL.replace("mongodb://","")
                strings=  str1.split(':')
                if(len(strings)==3):
                    database= strings[0];
                    dbName=   strings[1];
                    colName=  strings[2];
#                    print("database: ", database, "length: ", len(database))
#                    print("dbName: "  ,   dbName, "length: ", len(dbName))
#                    print("colName: " ,  colName, "length: ", len(colName))
                    ### must insert a better error detection here

                    if ((len(database)>0) and (len(dbName)>0) and (len(colName)>0)):


                        try:
#                            print("connecting: "+dbURL)
                            try:
                                myclient = pymongo.MongoClient("mongodb://"+ str(os.environ[database])+"/")
                                myclient.server_info()
                            except pymongo.errors.ServerSelectionTimeoutError as err:
                                print(err)
                                return "Ack: Could not connect to MongoDB: "+str(dbURL)

                            mydb = myclient[dbName]

                            mycol=mydb[colName]

                            # id=message['id']
                            newEntry=message['newEntry']

#                            print("newEntry",str(newEntry))
                            try:
                                # print("add newEntry")
                                # print("dbName:",dbName)
                                # print("colName:",colName)

                                 mydb[colName].insert_one(newEntry)
                            #
                            except Exception as e: print(e)
#                            print("done: "+dbURL)


                            return 'OK'
                        except:
                            print("could not connect to MongoDB: ",dbURL)
                            return "Ack: Could not connect to MongoDB: "+str(dbURL)

                else:
                    print("Malformed database URL, must be in format: mongodb://databaseID:database:collection")
            else:
                print("Unknown db type type: ",dbURL)
        else:
            print("write access denied to database URL: ", dbURL)

    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')




@socketio.on('AuthenticateClient', namespace='/pvServer')
def test_authorise(message):
    global REACT_APP_DisableLogin

    if (not REACT_APP_DisableLogin ):
        jwt=AuthenticateUser(message['user'])
        if not (jwt is None) :
            emit('clientAuthenticated', {'successful': True, 'jwt':jwt},room=request.sid,namespace='/pvServer')
        else:
            emit('clientAuthenticated', {'successful': False},room=request.sid,namespace='/pvServer')
            socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')
    else:
        emit('clientAuthenticated', {'successful': True, 'jwt':'anonomous'},room=request.sid,namespace='/pvServer')

@socketio.on('AuthoriseClient', namespace='/pvServer')
def test_authenticate(message):
    global REACT_APP_DisableLogin

    if (not REACT_APP_DisableLogin ):
        if  AuthoriseUser(message):
            emit('clientAuthorisation', {'successful': True},room=request.sid,namespace='/pvServer')
        else:
            emit('clientAuthorisation', {'successful': False},room=request.sid,namespace='/pvServer')
            socketio.emit('redirectToLogIn',room=request.sid,namespace='/pvServer')
            disconnect(request.sid,namespace='/pvServer')
    else:
        emit('clientAuthorisation', {'successful': True},room=request.sid,namespace='/pvServer')



@socketio.on('connect', namespace='/pvServer')
def test_connect():
    global thread
    print("Client Connected: " +request.sid)
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/pvServer')
def test_disconnect():
    print('Client disconnected', request.sid)
    disconnect(request.sid,namespace='/pvServer')


if __name__ == '__main__':
    REACT_APP_PyEpicsServerURL=os.getenv('REACT_APP_PyEpicsServerBASEURL')
    REACT_APP_PyEpicsServerPORT=os.getenv('REACT_APP_PyEpicsServerPORT')
    if (REACT_APP_PyEpicsServerPORT is None):
        REACT_APP_PyEpicsServerPORT='5000'

    REACT_APP_PyEpicsServerURL=REACT_APP_PyEpicsServerURL+':'+REACT_APP_PyEpicsServerPORT+'/'+'pvServer'
    print("pvServer URL: ",REACT_APP_PyEpicsServerURL)
    print("")
    if not (REACT_APP_PyEpicsServerURL is None):
        if 'https' in REACT_APP_PyEpicsServerURL:
            socketio.run(app, host='0.0.0.0', debug=True, port=int(REACT_APP_PyEpicsServerPORT,10), keyfile='../certificates/server.key', certfile='../certificates/server.cer',use_reloader=False)
        else:
            socketio.run(app,host='0.0.0.0',port=int(REACT_APP_PyEpicsServerPORT,10),  debug=True,use_reloader=False)
    else:
        socketio.run(app,host='127.0.0.1',  debug=True,use_reloader=False)
