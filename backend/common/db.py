from pymongo import MongoClient
import json
from bson import json_util
from common.config import *
from flask.json import JSONEncoder
from bson import json_util, ObjectId
from datetime import datetime

class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJsonEncoder, self).default(obj) 

config = Config()
mongo = MongoClient(config.mongo_uri)
