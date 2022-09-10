from flask import Flask
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask.json import JSONEncoder
from bson import json_util, ObjectId
from endpoints import api
from common.config import *
from common.db import *
    
def create_app(config):
    app = Flask(__name__)
    app.json_encoder = MongoJsonEncoder
    api.init_app(app)
    Bootstrap(app)
    CORS(app)
    
    return app




if __name__ == '__main__':
    config = Config()
    app = create_app(config)
    port = config.port
    if port is None:
        app.run(host='0.0.0.0', port=5010, debug=True)
    else:
        app.run(host='0.0.0.0', port=int(port), debug=True)