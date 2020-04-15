from pymongo import MongoClient
from pymongo.errors import OperationFailure
from time import sleep

client = MongoClient('localhost')

# wait to allow mongodbs to come up
sleep(5)

try:
    client.admin.command({"replSetGetStatus": 1})
    print("Replset already instantiated... skipping this step.")
    print("Mongo setup complete. Exiting mongosetup docker service. [mongodb still running!]")

except OperationFailure as err:
    print("Initialising new mongodb replset.")
    config_document = {
        "_id":
        "devrs",
        "members": [
            {
                "_id": 0,
                "host": "localhost:27017"
            },
            {
                "_id": 1,
                "host": "localhost:27018"
            },
            {
                "_id": 2,
                "host": "localhost:27019"
            },
        ]
    }

    client.admin.command({"replSetInitiate": config_document})
    print("Replset successfully instantiated.")
    print(client.admin.command({"replSetGetStatus": 1})["members"])
    print("Replset successfully instantiated.")
    print("Mongo setup complete. Exiting mongosetup docker service. [mongodb still running!]")

