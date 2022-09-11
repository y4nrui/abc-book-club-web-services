from wsgiref import validate
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from bson.objectid import ObjectId
from datetime import datetime
# from .db import get_db
# from flask import current_app, g
# from werkzeug.local import LocalProxy
# from flask_pymongo import PyMongo
# from pymongo import MongoClient
from common.db import *
import re

db = mongo['abc_books']
ns = Namespace('User', description='APIs for User management')

user = ns.model('User', {
    '_id': fields.String(required=False, description='The unique id of the user (auto-generated)'),
    'email': fields.String(required=True, description="The unique email of the user"),
    'name': fields.String(required=True, description="The name of the user"),
    'role': fields.String(required=True, description='The role of the user'),
    'date_joined': fields.DateTime(required=False, dt_format='iso8601', description='The date that the user joined in ISO format (auto-generated)'),
    'books_on_borrow': fields.List(fields.String(), required=False, description='The list of books (book_id) that the user is borrowed and has not returned')
    
})

class UserDAO(object):
    def __init__(self):
        self.users = db['users']
        
    def get(self, email):
        user = self.users.find_one({"email": re.compile(email, re.IGNORECASE)})
        return jsonify(user)
        ns.abort(404, "User {} doesn't exist".format(id))
        
    def get_all_same_role(self, role):
        user = self.users.find({"role": re.compile(role, re.IGNORECASE)})
        result = list(user)
        res = {'result': result, 'response': "200"}
        return jsonify(res)
        ns.abort(404, "User {} doesn't exist".format(id))

    def create(self, data):
        user = data
        user.pop('_id', None)
        current_datetime = datetime.now().isoformat()
        user['date_joined'] = current_datetime # current local datetime in iso format
        self.users.insert_one(user)

    def update(self, email, data):
        user = data
        user.pop('_id', None) # mongodb objectid can't be changed
        user.pop('date_joined', None) # date_joined won't be changed
        result = self.users.update_one({'email': email}, {'$set': data}, True)
        return result.raw_result
        
    def delete(self, email):
        user = self.users.delete_one({'email': email })
        #return user.raw_result
    
DAO = UserDAO()

@ns.route('/user') # input parameter
class UsersList(Resource):
    """GET all users, and POST a new user"""
    @ns.doc('get_all_users')
    def get(self):  # input parameter
        """Get all users"""
        result = list((DAO.users.find()))
        res = {'result': result, 'response': "200"}
        return jsonify(res)

    @ns.doc('create_a_user')
    @ns.expect(user, validate=False)
    def post(self):
        """Create a new user"""
        print(ns.payload)
        return DAO.create(ns.payload), 201

@ns.route('/user/<email>') # input parameter
@ns.param('email', 'The email of the user (str)')
@ns.response(404, 'User not found')
class Users(Resource):
    """Fetch a single user, update a user, or delete a user based on their email"""
    @ns.doc('get_a_user')
    def get(self, email): # input parameter
        """Fetch a user by email"""
        return DAO.get(email)
    
    @ns.doc('delete_a_user')
    def delete(self, email):
        """Delete a given user by its email"""
        DAO.delete(email)
        return "", 204

    @ns.doc('update_a_user')
    @ns.expect(user, validate=False)
    def put(self, email):
        """Update a given user by its email"""
        return DAO.update(email, ns.payload)
    
@ns.route('/get_users_of_same_role/<role>') # input parameter
@ns.param('role', 'The role of the user (str)')
@ns.response(404, 'User not found')
class ManyUsers(Resource):
    @ns.doc('get_all_user_of_the_same_role')
    def get(self, role): # input parameter
        """Fetch all users that have the same role"""
        return DAO.get_all_same_role(role)