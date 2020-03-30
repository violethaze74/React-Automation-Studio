#!/usr/bin/env python
import gevent
from gevent import monkey; monkey.patch_all()
import time
import pymongo

import threading
import numpy as np
from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from bson.json_util import dumps


import pyads
import logging
import os
import sys
import json
import platform    # For getting the operating system name
import subprocess  # For executing a shell command

from functools import partial
from bson.objectid import ObjectId


from dotenv import load_dotenv
from ctypes import memmove, addressof, c_ubyte,c_int, Structure, sizeof
from pyads.structs import SAdsNotificationHeader
import ctypes
import struct
#from ratelimiter import RateLimiter
load_dotenv()
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = 'gevent'
print("")
print('**************************************')
print("React Automation Studio V1.2.3")
print("")
print("adsServer Environment Variables:")
print("")

print('adsServerBASEURL: '+ str(os.environ['adsServerBASEURL']))
print('adsServerPORT: '+ str(os.environ['adsServerPORT']))
print('REACT_APP_PyEpicsServerNamespace: '+ str(os.environ['REACT_APP_PyEpicsServerNamespace']))


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






socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread2 = None
thread_lock = threading.Lock()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)



clientPVlist={};
clientDbWatchList={};
clientAdsPlcList={};
plcPVlist={};
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
def sync_update():
    global plcPVlist
    while True:
        #print("sync_update")
        for pv in plcPVlist:
            #print("pv",pv)
            #print("pv newData",plcPVlist[pv]['newData'])
            if plcPVlist[pv]['newData']==True:
                notification=plcPVlist[pv]['notification']
                name=plcPVlist[pv]['name']
                pvname=plcPVlist[pv]['pvname']
                datatype=plcPVlist[pv]['datatype']
                isArray=plcPVlist[pv]['isArray']
                connected=plcPVlist[pv]['connected']
                arraySize=plcPVlist[pv]['arraySize']
                contents = notification.contents
                epoch_diff = 116444736000000000;
                rate_diff = 10000000;
                timestamp=(contents.nTimeStamp-epoch_diff)/rate_diff
                #print(timestamp)

                data_size = contents.cbSampleSize
                data = (c_ubyte * data_size).from_address(addressof(contents) + SAdsNotificationHeader.data.offset)
                #print("data",data)
                value = bytearray(data)
                #print("value",value[0],value[1] )
                if datatype in ["BOOL"]:
                    #print("AdsCallback emitting",pvname)
                    x=int.from_bytes(value, byteorder='little', signed=True)
                    socketio.emit('adsData',
                       {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':connected, 'severity': 0,'timestamp':timestamp
                       },room=str(pvname),namespace='/adsServer')
                elif datatype in ["INT"]:
                    #print("AdsCallback emitting",pvname)
                    if not isArray:
                        x=int.from_bytes(value, byteorder='little', signed=True)
                        socketio.emit('adsData',
                           {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':connected, 'severity': 0,'timestamp':timestamp
                           },room=str(pvname),namespace='/adsServer')
                    else:
                        length=contents.cbSampleSize/2;
                        #print("isArray",pvname,"cbsize",contents.cbSampleSize,struct.unpack('hh', value[0:3]))
                        #print("isArray all data",str(value))
                        #print(len(value))
                        #print(len(value[0:16]));
                        length=str(int((len(value)/2)))
                        data=struct.unpack("<"+length+"h",value)
                        socketio.emit('adsData',
                           {'pvname': pvname,'newmetadata': 'True','value': data,'char_value': str(data),'count':int(length), 'connected':connected, 'severity': 0,'timestamp':timestamp
                           },room=str(pvname),namespace='/adsServer')
                        #print("isArray value",struct.unpack('hh', value[0:7]))

                elif datatype in ["LINT"]:
                    #print("data_size",data_size)
                    x=int.from_bytes(value, byteorder='little', signed=True)
                    socketio.emit('adsData',
                       {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':connected, 'severity': 0,'timestamp':timestamp
                       },room=str(pvname),namespace='/adsServer')
                elif datatype in ["REAL"]:
                    #print("data_size",data_size)
                    #x=float.from_bytes(value, byteorder='little', signed=True)
                    x=struct.unpack('<f', value)
                    socketio.emit('adsData',
                       {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':connected, 'severity': 0,'timestamp':timestamp
                       },room=str(pvname),namespace='/adsServer')
                elif datatype in ["LREAL"]:
                    #print("data_size",data_size)
                    #x=float.from_bytes(value, byteorder='little', signed=True)
                    x=struct.unpack('<d', value)
                    socketio.emit('adsData',
                       {'pvname': pvname,'newmetadata': 'True','value': x,'char_value': str(x),'count':1, 'connected':connected, 'severity': 0,'timestamp':timestamp
                       },room=str(pvname),namespace='/adsServer')
                else:
                    print("undeifned callback datatype:",datatype)


                plcPVlist[pv]['newData']=False;
        time.sleep(0.1)

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
                              socketio.emit(pvname,d,room=rw_room,namespace='/adsServer')
                              d['write_access']=False
                              ro_room=str(pvname)+'ro'
                              socketio.emit(pvname,d,room=ro_room,namespace='/adsServer')
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

                              socketio.emit(pvname,d,room=str(pvname),namespace='/adsServer')
                          except:
                              print("Unexpected error:", sys.exc_info()[0])
                              raise
                  elif ('ads://' in pvname):
                      print("check_pv_initialized_after_disconnect:",pvname)
       for plcName in clientAdsPlcList :
           if not 'plc' in clientAdsPlcList[plcName]:
               print("check_pv_initialized_after_disconnect: No PLC object:",plcName)

           else:
               if clientAdsPlcList[plcName]['state']=='opened':
                   #isOpen=clientAdsPlcList[plcName]['plc'].is_open;
                   #print(plcName," is open: ",isOpen)
                   try:
                       state=clientAdsPlcList[plcName]['plc'].read_state();
                       print("plc state",state)
                       clientAdsPlcList[plcName]['state']='running'



                   except:
                       clientAdsPlcList[plcName]['state']=='readStateError'
               elif clientAdsPlcList[plcName]['state']=='running':
                    #isOpen=clientAdsPlcList[plcName]['plc'].is_open;
                    #print(plcName," is open: ",isOpen)
                   try:
                       state=clientAdsPlcList[plcName]['plc'].read_state();
                       print(plcName,clientAdsPlcList[plcName]['state'],"plc state",state)
                       clientAdsPlcList[plcName]['state']='running'



                   except:
                       clientAdsPlcList[plcName]['state']='readStateError'
                       print(plcName,clientAdsPlcList[plcName]['state'],"plc next state",'readStateError')
                       try:
                            print("delete_route: ",clientAdsPlcList[plcName]['PlcAmsID'] )
                            clientAdsPlcList[plcName]['plc'].delete_route(clientAdsPlcList[plcName]['PlcAmsID']);
                            for handles in clientAdsPlcList[plcName]['plc']['notificationHandles']:
                                clientAdsPlcList[plcName]['plc'].del_device_notification(*handle)
                            clientAdsPlcList[plcName]['plc'].close_port();
                            clientAdsPlcList[plcName]['plc'].close();

                       except:
                            print("123123closing previous connection failed:",plcName)





               elif clientAdsPlcList[plcName]['state']=='readStateError':
                   print(plcName,clientAdsPlcList[plcName]['state'])
                   print("can't read state from: ",plcName," restarting")
                   print("exiting")
                   socketio.stop()
                   os._exit(0)

                   #plcPinAlive=ping(clientAdsPlcList[plcName]['PlcIP'])
                   #if plcPinAlive:
                #       print("can't read state from: ",plcName," restarting")
                    #   clientAdsPlcList[plcName]['state']='pingedAlive'
                #       print("exiting")
                #       socketio.stop()
                       #sys.exit()
                #       os._exit(0)

               #
               # elif clientAdsPlcList[plcName]['state']=='pingedAlive':
               #     print("closing previous connection to:",plcName)
               #     try:
               #         #clientAdsPlcList[plcName]['plc'].close();
               #         clientAdsPlcList[plcName]['state']='closed'
               #     except:
               #         print("closing previous connection failed:",plcName)
               #         clientAdsPlcList[plcName]['state']='reconnect'
               #
               # elif clientAdsPlcList[plcName]['state']=='closed':
               #     #print("closed, but checking is_open:",plcName,clientAdsPlcList[plcName]['plc'].is_open)
               #     clientAdsPlcList[plcName]['state']='reconnect'
               #     clientAdsPlcList[plcName]['plc']=None;
               # elif clientAdsPlcList[plcName]['state']=='reconnect':
               #     #importlib.reload(pyads)
               #     print("PCL pinged alive attempting to establish an ads connection:",plcName)
               #     pyads.open_port();
               #     pyads.add_route_to_plc(clientAdsPlcList[plcName]['hostAmsID'], clientAdsPlcList[plcName]['hostIp'], clientAdsPlcList[plcName]['PlcIP'], clientAdsPlcList[plcName]['username'], clientAdsPlcList[plcName]['password'], route_name=clientAdsPlcList[plcName]['hostIp'],added_net_id=clientAdsPlcList[plcName]['hostAmsID'])
               #     clientAdsPlcList[plcName]['routeAdded']=True;
               #     clientAdsPlcList[plcName]['connectionAdded']=True;
               #     plc = pyads.Connection(clientAdsPlcList[plcName]['PlcAmsID'], 851, clientAdsPlcList[plcName]['PlcIP'])
               #     plc.set_timeout(5000)
               #
               #     clientAdsPlcList[plcName]['plc']=plc;
               #     clientAdsPlcList[plcName]['connectionAdded']=True;
               #
               #     clientAdsPlcList[plcName]['plc'].open()
               #     clientAdsPlcList[plcName]['state']='opened';
               #     clientAdsPlcList[plcName]['plcOpened']=True;


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
              },room='pva://'+str(pvname),namespace='/adsServer')
        else:
           d={'pvname': pvname1,'newmetadata': 'False','value': list((value)),'count':count, 'connected':'1', 'severity': severity,'timestamp':timestamp}
           socketio.emit(pvname1,d,room='pva://'+str(pvname),namespace='/adsServer')


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
            socketio.emit(pvname1,d,room=str(pvname1),namespace='/adsServer')
        except:
            error=2



def background_thread():

    count = 0
    threading.Thread(target=check_pv_initialized_after_disconnect).start()

    while True:
        socketio.sleep(0.1)





@socketio.on('write_to_pv', namespace='/adsServer')
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



            else: print("Unknown PV type")
        else:
            print("***PV put error: write access denied ")
            print("PV name: "+ str(message['pvname']))
            print("Value to put : "+str(message['data']))
    else:
        socketio.emit('redirectToLogIn',room=request.sid,namespace='/adsServer')




def AdsCallback(notification,name,pvname,datatype,isArray,arraySize):
        global plcPVlist


        pv={}
        pv['notification']=notification
        pv['name']=name
        pv['pvname']=pvname
        pv['datatype']=datatype
        pv['isArray']=isArray
        pv['arraySize']=arraySize
        pv['connected']='1'
        pv['newData']=True
        plcPVlist[pvname]=pv;


###########

@socketio.on('request_pv_info', namespace='/adsServer')
def test_message(message):
    global plcPVlist,REACT_APP_DisableLogin,clientAdsPlcList
    pvname1= str(message['data'])


    if True :

        
        if not (pvname1 in	plcPVlist):

            if "ads://" in pvname1:

                print("ads request 0")
                print("ads pvname1",pvname1)

                str1=pvname1.replace("ads://","")
                strings=  str1.split(':')
                #print(strings)
                try:
                    if(len(strings)>=4):
                        plcName= strings[0];
                        plcPort=   strings[1];
                        plcVariable=  strings[2];
                        plcVariableType= strings[3];
                        try:
                            if '[' in plcVariableType:
                                plcVariableType=plcVariableType.replace('[',':');
                                plcVariableType=plcVariableType.replace(']','');
                                plcVariableTypeString=plcVariableType.split(':');
                                plcVariableType=plcVariableTypeString[0];
                                plcVariableTypeArraySize=int(plcVariableTypeString[1],10)
                                plcVariableTypeIsArray=True
                            else:
                                plcVariableTypeIsArray=False
                                plcVariableTypeArraySize=1;


                        except:
                            plcVariableTypeIsArray=False
                            plcVariableTypeArraySize=1;
                        if not (plcName in	clientAdsPlcList):
                            try:
                                clientAdsPlcList[plcName]={};
                                clientAdsPlcList[plcName]['state']='POR';
                                clientAdsPlcList[plcName]['isConnected']=False;
                                clientAdsPlcList[plcName]['isDisconnected']=True;
                                clientAdsPlcList[plcName]['routeAdded']=False;
                                clientAdsPlcList[plcName]['connectionAdded']=False;
                                clientAdsPlcList[plcName]['plcOpened']=False;
                                clientAdsPlcList[plcName]['readStateError']=False;
                                plcConfigUsername=str(os.environ['ADS_PLC_USERNAME_'+plcName]);
                                plcConfigPassword=str(os.environ['ADS_PLC_PASSWORD_'+plcName]);
                                plcConfigPlcAmsID=str(os.environ['ADS_PLC_AMS_ID_'  +plcName]);
                                plcConfigPlcIP=str(os.environ['ADS_PLC_IP_'         +plcName]);
                                plcConfigHostIP=str(os.environ['ADS_HOST_IP']);
                                clientAdsPlcList[plcName]['notificationHandles']=[];
                                clientAdsPlcList[plcName]['username']=plcConfigUsername;
                                clientAdsPlcList[plcName]['password']=plcConfigPassword;
                                clientAdsPlcList[plcName]['PlcAmsID']=plcConfigPlcAmsID;
                                clientAdsPlcList[plcName]['PlcIP']=plcConfigPlcIP;
                                clientAdsPlcList[plcName]['hostIp']=plcConfigHostIP;
                                clientAdsPlcList[plcName]['hostAmsID']=plcConfigHostIP+'.1.1';

                                #pyads.add_route_to_plc('172.16.5.52.1.1', '172.16.5.52', clientAdsPlcList[plcName]['PlcIP'], clientAdsPlcList[plcName]['username'], clientAdsPlcList[plcName]['password'], route_name='172.16.5.52',added_net_id='172.16.5.52.1.1')
                                #pyads.add_route_to_plc('172.16.5.52.1.1', '172.16.5.52', '172.16.5.140', 'Administrator', '1', route_name='172.16.5.52',added_net_id='172.16.5.52.1.1')
                                #clientAdsPlcList[plcName]['plc']=pyads.Connection('172.15.5.140.1.1', 851,'172.16.5.140')

                                pyads.add_route_to_plc(clientAdsPlcList[plcName]['hostAmsID'], clientAdsPlcList[plcName]['hostIp'], clientAdsPlcList[plcName]['PlcIP'], clientAdsPlcList[plcName]['username'], clientAdsPlcList[plcName]['password'], route_name=clientAdsPlcList[plcName]['hostIp'],added_net_id=clientAdsPlcList[plcName]['hostAmsID'])
                                clientAdsPlcList[plcName]['routeAdded']=True;
                                clientAdsPlcList[plcName]['connectionAdded']=True;
                                plc = pyads.Connection(clientAdsPlcList[plcName]['PlcAmsID'], 851, clientAdsPlcList[plcName]['PlcIP'])
                                plc.set_timeout(5000)

                                clientAdsPlcList[plcName]['plc']=plc;
                                clientAdsPlcList[plcName]['connectionAdded']=True;

                                clientAdsPlcList[plcName]['plc'].open()
                                clientAdsPlcList[plcName]['state']='opened';
                                clientAdsPlcList[plcName]['plcOpened']=True;
                                print("opened",plc.is_open)
                            except Exception as e: # work on python 3.x
                                print(' could not add route and load plc info ' + str(plcName)+' '+ str(e))
                        else:
                            print("route to plc "+plcName+' already exists')
                            #print(clientAdsPlcList[plcName])

                        try:

                            while not 'plc' in clientAdsPlcList[plcName]:
                                print("conecting to PLC:", plcName)
                                time.sleep(0.1)
                            while clientAdsPlcList[plcName]['plc'].is_open==False:
                                print("conecting to PLC:", plcName)
                                time.sleep(0.1)
                            if plcVariableType=='BOOL' :
                                plcVariablePyAdsType=pyads.PLCTYPE_BOOL;
                                attr = pyads.NotificationAttrib(sizeof(plcVariablePyAdsType))
                                handle=clientAdsPlcList[plcName]['plc'].add_device_notification(plcVariable, attr, partial(AdsCallback, pvname=pvname1,datatype=plcVariableType,isArray=plcVariableTypeIsArray,arraySize=plcVariableTypeArraySize))
                                clientAdsPlcList[plcName]['notificationHandles'].append(handle)
                            elif plcVariableType=='INT' :
                                plcVariablePyAdsType=pyads.PLCTYPE_INT;
                                attr = pyads.NotificationAttrib(sizeof(plcVariablePyAdsType*plcVariableTypeArraySize))
                                handle=clientAdsPlcList[plcName]['plc'].add_device_notification(plcVariable, attr, partial(AdsCallback, pvname=pvname1,datatype=plcVariableType,isArray=plcVariableTypeIsArray,arraySize=plcVariableTypeArraySize))
                                clientAdsPlcList[plcName]['notificationHandles'].append(handle)
                            elif plcVariableType=='LINT' :

                                attr = pyads.NotificationAttrib(4)
                                handle=clientAdsPlcList[plcName]['plc'].add_device_notification(plcVariable, attr, partial(AdsCallback, pvname=pvname1,datatype=plcVariableType,isArray=plcVariableTypeIsArray,arraySize=plcVariableTypeArraySize))
                                clientAdsPlcList[plcName]['notificationHandles'].append(handle)
                            elif plcVariableType=='REAL' :
                                plcVariablePyAdsType=pyads.PLCTYPE_REAL;
                                attr = pyads.NotificationAttrib(sizeof(plcVariablePyAdsType))
                                handle=clientAdsPlcList[plcName]['plc'].add_device_notification(plcVariable, attr, partial(AdsCallback, pvname=pvname1,datatype=plcVariableType,isArray=plcVariableTypeIsArray,arraySize=plcVariableTypeArraySize))
                                clientAdsPlcList[plcName]['notificationHandles'].append(handle)
                            elif plcVariableType=='LREAL' :
                                plcVariablePyAdsType=pyads.PLCTYPE_LREAL;
                                attr = pyads.NotificationAttrib(sizeof(plcVariablePyAdsType))
                                handle=clientAdsPlcList[plcName]['plc'].add_device_notification(plcVariable, attr, partial(AdsCallback, pvname=pvname1,datatype=plcVariableType,isArray=plcVariableTypeIsArray,arraySize=plcVariableTypeArraySize))
                                clientAdsPlcList[plcName]['notificationHandles'].append(handle)
                            else:
                                Exception("unknown plc variable type");


                        except Exception as e: # work on python 3.x
                            print(' 2 could not load plc variable type ' + str(plcName)+' '+ str(e))

                    join_room(str(pvname1))
                except:
                     raise Exception("Malformed ads URL, must be in format: ads://plcName:plcPort:plcVariable:plcVariableType")





            else:
                print("Unknown PV type")


        else:

            if "ads://" in pvname1:
                print("pv exists alread",pvname1)
                if plcPVlist[pvname1]['connected']=='1':
                    plcPVlist[pvname1]['newData']=True  
                else:
                    print("pv exists alread but not connected",pvname1)      
                join_room(str(pvname1))
            else: print("Unknown PV type")


@socketio.on('write_by_name', namespace='/adsServer')
def test_message(message):
    global clientPVlist,REACT_APP_DisableLogin,clientAdsPlcList
    pvname1= str(message['pvname'])


    if True :


        if not (pvname1 in	clientPVlist):

            if "ads://" in pvname1:

                print("ads request 0")
                print("ads pvname1",pvname1)

                str1=pvname1.replace("ads://","")
                strings=  str1.split(':')
                #print(strings)
                try:
                    if(len(strings)>=4):
                        plcName= strings[0];
                        plcPort=   strings[1];
                        plcVariable=  strings[2];
                        plcVariableType= strings[3];
                        if not (plcName in	clientAdsPlcList):
                            try:
                                clientAdsPlcList[plcName]={};
                                clientAdsPlcList[plcName]['state']='POR';
                                clientAdsPlcList[plcName]['isConnected']=False;
                                clientAdsPlcList[plcName]['isDisconnected']=True;
                                clientAdsPlcList[plcName]['routeAdded']=False;
                                clientAdsPlcList[plcName]['connectionAdded']=False;
                                clientAdsPlcList[plcName]['plcOpened']=False;
                                clientAdsPlcList[plcName]['readStateError']=False;
                                plcConfigUsername=str(os.environ['ADS_PLC_USERNAME_'+plcName]);
                                plcConfigPassword=str(os.environ['ADS_PLC_PASSWORD_'+plcName]);
                                plcConfigPlcAmsID=str(os.environ['ADS_PLC_AMS_ID_'  +plcName]);
                                plcConfigPlcIP=str(os.environ['ADS_PLC_IP_'         +plcName]);
                                plcConfigHostIP=str(os.environ['ADS_HOST_IP']);
                                clientAdsPlcList[plcName]['notificationHandles']=[];
                                clientAdsPlcList[plcName]['username']=plcConfigUsername;
                                clientAdsPlcList[plcName]['password']=plcConfigPassword;
                                clientAdsPlcList[plcName]['PlcAmsID']=plcConfigPlcAmsID;
                                clientAdsPlcList[plcName]['PlcIP']=plcConfigPlcIP;
                                clientAdsPlcList[plcName]['hostIp']=plcConfigHostIP;
                                clientAdsPlcList[plcName]['hostAmsID']=plcConfigHostIP+'.1.1';

                                #pyads.add_route_to_plc('172.16.5.52.1.1', '172.16.5.52', clientAdsPlcList[plcName]['PlcIP'], clientAdsPlcList[plcName]['username'], clientAdsPlcList[plcName]['password'], route_name='172.16.5.52',added_net_id='172.16.5.52.1.1')
                                #pyads.add_route_to_plc('172.16.5.52.1.1', '172.16.5.52', '172.16.5.140', 'Administrator', '1', route_name='172.16.5.52',added_net_id='172.16.5.52.1.1')
                                #clientAdsPlcList[plcName]['plc']=pyads.Connection('172.15.5.140.1.1', 851,'172.16.5.140')

                                pyads.add_route_to_plc(clientAdsPlcList[plcName]['hostAmsID'], clientAdsPlcList[plcName]['hostIp'], clientAdsPlcList[plcName]['PlcIP'], clientAdsPlcList[plcName]['username'], clientAdsPlcList[plcName]['password'], route_name=clientAdsPlcList[plcName]['hostIp'],added_net_id=clientAdsPlcList[plcName]['hostAmsID'])
                                clientAdsPlcList[plcName]['routeAdded']=True;
                                clientAdsPlcList[plcName]['connectionAdded']=True;
                                plc = pyads.Connection(clientAdsPlcList[plcName]['PlcAmsID'], 851, clientAdsPlcList[plcName]['PlcIP'])
                                plc.set_timeout(5000)

                                clientAdsPlcList[plcName]['plc']=plc;
                                clientAdsPlcList[plcName]['connectionAdded']=True;

                                clientAdsPlcList[plcName]['plc'].open()
                                clientAdsPlcList[plcName]['state']='opened';
                                clientAdsPlcList[plcName]['plcOpened']=True;
                                print("opened",plc.is_open)
                            except Exception as e: # work on python 3.x
                                print(' could not add route and load plc info ' + str(plcName)+' '+ str(e))
                        else:
                            print("route to plc "+plcName+' already exists')
                            #print(clientAdsPlcList[plcName])

                        try:

                            while not 'plc' in clientAdsPlcList[plcName]:
                                print("conecting to PLC:", plcName)
                                time.sleep(0.1)
                            while clientAdsPlcList[plcName]['plc'].is_open==False:
                                print("conecting to PLC:", plcName)
                                time.sleep(0.1)
                            if plcVariableType=='BOOL' :
                                plcVariablePyAdsType=pyads.PLCTYPE_BOOL;
                                if isinstance(message['data'],int):
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,message['data'],plcVariablePyAdsType)
                                else:
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,int(message['data'],10),plcVariablePyAdsType)
                            elif plcVariableType=='INT' :
                                plcVariablePyAdsType=pyads.PLCTYPE_INT;
                                if isinstance(message['data'],int):
                                    data=np.int32(message['data']);
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,plcVariablePyAdsType)
                                else:
                                    data=np.int32(int(message['data'],10))

                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,plcVariablePyAdsType)
                            elif plcVariableType=='LINT' :

                                attr = pyads.NotificationAttrib(4)
                                if isinstance(message['data'],int):
                                    data=np.int64(message['data']);
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,ctypes.c_int64)
                                else:
                                    data=np.int64(int(message['data'],10))
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,ctypes.c_int64)
                            elif plcVariableType=='REAL' :
                                plcVariablePyAdsType=pyads.PLCTYPE_REAL;

                                if isinstance(message['data'],float):
                                    data=np.float32(message['data']);
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,plcVariablePyAdsType)
                                else:
                                    data=np.float32(float(message['data']))

                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,plcVariablePyAdsType)
                            elif plcVariableType=='LREAL' :
                                plcVariablePyAdsType=pyads.PLCTYPE_LREAL;
                                if isinstance(message['data'],float):
                                    data=np.float64(message['data']);
                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,plcVariablePyAdsType)
                                else:
                                    data=np.float64(float(message['data']))

                                    clientAdsPlcList[plcName]['plc'].write_by_name(plcVariable,data,plcVariablePyAdsType)

                            else:
                                Exception("unknown plc variable type");


                        except Exception as e: # work on python 3.x
                            print(' 2 could not load plc variable type ' + str(plcName)+' '+ str(e))


                except:
                     raise Exception("Malformed ads URL, must be in format: ads://plcName:plcPort:plcVariable:plcVariableType")





            else:
                print("Unknown PV type")


        else:

            if "ads://" in pvname1:
                print("pv exista alread",pvname1)

            else: print("Unknown PV type")



@socketio.on('connect', namespace='/adsServer')
def test_connect():
    global thread, thread2
    print("Client Connected: " +request.sid)
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
        if thread2 is None:
            thread = socketio.start_background_task(sync_update)

    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/adsServer')
def test_disconnect():
    print('Client disconnected', request.sid)
    disconnect(request.sid,namespace='/adsServer')


if __name__ == '__main__':
    REACT_APP_PyEpicsServerURL=os.getenv('adsServerBASEURL')
    adsServerPORT=os.getenv('adsServerPORT')
    if (adsServerPORT is None):
        adsServerPORT='5002'

    REACT_APP_PyEpicsServerURL=REACT_APP_PyEpicsServerURL+':'+adsServerPORT+'/'+'pvServer'
    print("pvServer URL: ",REACT_APP_PyEpicsServerURL)
    print("")
    #if not (REACT_APP_PyEpicsServerURL is None):
    #    if 'https' in REACT_APP_PyEpicsServerURL:
    #        socketio.run(app, host='0.0.0.0', debug=True, port=int(adsServerPORT,10), keyfile='../certificates/server.key', certfile='../certificates/server.cer',use_reloader=False)
    #    else:
    socketio.run(app,host='0.0.0.0',port=int(adsServerPORT,10),  debug=True,use_reloader=False)
    #else:
    #    socketio.run(app,host='127.0.0.1',  debug=True,use_reloader=False)
