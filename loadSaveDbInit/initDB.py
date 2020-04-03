import pymongo
import sys
import os
import configparser
path='savedConfig/'
sys.path.insert(0,path )
# print("hello")
#
# myclient = pymongo.MongoClient("mongodb://database:27017/")
# dblist = myclient.list_database_names()
# if "mydatabase" in dblist:
#     print("The database exists.")
# else:
#     mydb = myclient["mydatabase"]
#     mycol = mydb["customers"]
#     mydict = { "name": "John", "address": "Highway 37" }
#     x = mycol.insert_one(mydict)
#
# print(myclient.list_database_names())
databaseName='testIOCSystems'
myclient = pymongo.MongoClient("mongodb://loadsavedb:27017/")
mydb = myclient[databaseName]
filenames= os.listdir('listOfSavePVs/')

print("filename entries: ",filenames)
for filename in filenames:
    print("###########")
    print("filename :",filename)
    systemName=filename.replace("_Save_PVs.txt","")
    print("systemname: ",systemName)
    system={}
    system['name']=systemName
    system['keys']={}
    system['PVs']={}

    with open('listOfSavePVs/'+filename) as f:
        content = f.readlines()
        keys=[]

        for line in content:
            line=line.replace("\n","")

            key=line
            newKey=line.replace(systemName+":","")
            newKey=newKey.replace(systemName+"_RFM_","")
            newKey=newKey.replace("_"," ")
        #    print(newKey)
            newKey=newKey.replace(":"," ")
            newKey=newKey.replace("."," ")
            newKey=newKey.capitalize()
            newKey=newKey.replace("Rf","RF")
            newKey=newKey.replace("rf","RF")
            newKey=newKey.replace("pid","PID")
            newKey=newKey.replace("oroc","OROC")
            newKey=newKey.replace("pa","PA")
            newKey=newKey.replace("dbm","dBm")
            newKey=newKey.replace("kp","Kp")
            newKey=newKey.replace("ki","Ki")
            newKey=newKey.replace("kd","Kd")
            system['keys'][newKey]=newKey
            system['PVs'][newKey]={}
            system['PVs'][newKey]['pvName']="pva://"+line
            system['PVs'][newKey]['description']=newKey

        #    print(key,": ",newKey)
        #print("system: ",system)
        dict={}
        dict['process_variables']=system['PVs']
        mycol = mydb[system['name']+'_PVs']
        x = mycol.insert_one(dict)
        folder='savedConfig/'+system['name']+'/'
        entries = os.listdir(folder)
        #print(entries)
        for entry in entries:
            #print("Folder: ", folder, " entry: ", entry )
            settings = configparser.ConfigParser()
            settings.optionxform = str
            settings._interpolation = configparser.ExtendedInterpolation()
            settings.read(folder+entry)
            #print(settings.sections())
            #print(settings.items('beam_setup'))
            items=settings.items('beam_setup');
            dict={};
            dict['beam_setup']={}
            for item in items:
                dict['beam_setup'][item[0]]=item[1]


            #print(settings.items('process_variables'))
            items=settings.items('process_variables');
            dict['process_variables']={};
            for item in items:
                newKey=item[0].replace(systemName+"_","")
                newKey=newKey.replace("RFM_","")
                newKey=newKey.replace("_"," ")
            #    print(newKey)
                newKey=newKey.replace(":"," ")
                newKey=newKey.replace("."," ")
                newKey=newKey.capitalize()
                newKey=newKey.replace("Rf","RF")
                newKey=newKey.replace("rf","RF")
                newKey=newKey.replace("pid","PID")
                newKey=newKey.replace("oroc","OROC")
                newKey=newKey.replace("pa","PA")
                newKey=newKey.replace("dbm","dBm")
                newKey=newKey.replace("kp","Kp")
                newKey=newKey.replace("ki","Ki")
                newKey=newKey.replace("kd","Kd")
                try:
                    #pvName=item[0].replace(system['name']+'_','pva://'+system['name']+':');
                    pvName=system['PVs'][newKey]['pvName'];
                    pvValue=item[1];
                    dict['process_variables'][system['keys'][newKey]]={'pvName':pvName,'pvValue':pvValue};
                except:
                    print(newKey, "  Unknown Key in: ",folder,entry)
                #key=key.replace("."," ");

                #ict['process_variables'][key]={'pvName':pvName,'pvValue':pvValue};
            print(dict)

            #myclient = pymongo.MongoClient("mongodb://database:27017/")
            mydb = myclient[databaseName]
            mycol = mydb[system['name']+'_DATA']
            x = mycol.insert_one(dict)
