# from flask import Flask
# from flask_bootstrap import Bootstrap
# from flask_cors import CORS

# # from backend.common import db
# # from flask_pymongo import PyMongo
# from .common.db import mongo
# from endpoints import api
# import os

# def create_app(config):
#     app = Flask(__name__)
#     api.init_app(app)

#     app.config["MONGO_URI"] = config.mongo_uri
#     mongo.init_app(app)
#     db = mongo.db

#     Bootstrap(app)
#     CORS(app)

#     return app