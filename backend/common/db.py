from pymongo import MongoClient
import json
from bson import json_util
from common.config import *

config = Config()
mongo = MongoClient(config.mongo_uri)
