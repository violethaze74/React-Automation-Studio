from pymongo import MongoClient
from pymongo.errors import OperationFailure
from time import sleep


def masterStepUp():
    ismaster = client.admin.command({"ismaster": 1})["ismaster"]
    print("Waiting for mongodb PRIMARY to step up.")
    while (not ismaster):
        ismaster = client.admin.command({"ismaster": 1})["ismaster"]
    print("mongodb PRIMARY has successfully stepped up.")


client = MongoClient('localhost')

sleep(5)

try:
    client.admin.command({"replSetGetStatus": 1})
    print("Replset already instantiated... skipping this step.")
    masterStepUp()

except OperationFailure as err:
    print("Initialising new mongodb replset.")
    config_document = {
        "_id":
        "devrs",
        "members": [
            {
                "_id": 0,
                "host": "mongo1:27017"
            },
            {
                "_id": 1,
                "host": "mongo2:27017"
            },
            {
                "_id": 2,
                "host": "mongo3:27017"
            },
        ]
    }

    client.admin.command({"replSetInitiate": config_document})

    conf = client.admin.command({"replSetGetConfig": 1})["config"]

    conf["members"][0]["priority"] = 1.0
    conf["members"][1]["priority"] = 0.0
    conf["members"][2]["priority"] = 0.0

    client.admin.command({"replSetReconfig": conf, "force": True})

    masterStepUp()