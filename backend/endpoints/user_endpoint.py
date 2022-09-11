#from wsgiref import validate
from http import HTTPStatus
from flask_restx import Namespace, Resource, fields, abort
from flask_restx.reqparse import RequestParser
from flask_restx.inputs import email
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
# import time
import re
import json
from bson.objectid import ObjectId
from datetime import datetime, timedelta
# from .db import get_db
# from flask import current_app, g
# from werkzeug.local import LocalProxy
# from flask_pymongo import PyMongo
# from pymongo import MongoClient
from common.db import *
from common.config import Config

db = mongo['abc_books']
config = Config()
ns = Namespace('User', description='APIs for User management')

user = ns.model('User', {
    '_id': fields.String(required=False, description='The unique id of the user (auto-generated)'),
    'email': fields.String(required=True, description="The unique email of the user"),
    'password': fields.String(required=True, description="The password of the user in plain-text, password will be hashed when stored in db"),
    'name': fields.String(required=True, description="The name of the user"),
    'role': fields.String(required=True, description='The role of the user'),
    'date_joined': fields.DateTime(required=False, dt_format='iso8601', description='The date that the user joined in ISO format (auto-generated)'),
    'books_on_borrow': fields.List(fields.String(), required=False, description='The list of books (book_id) that the user is borrowed and has not returned')
})

class UserDAO(object):
    def __init__(self):
        self.users = db['users']
        self.users_change_approval = db['users_change_approval']
        
    def encode_access_token(self, user):
        now = datetime.now()
        user_role = user['role']
        user_email = user['email']
        token_expire_minutes = config.token_expire_minutes
        expire = now + timedelta(minutes=token_expire_minutes) # set token expiry (default is 5mins)
        payload = dict(exp=expire, iat=now, user_email=user_email, user_role=user_role)
        key = config.secret_key
        return jwt.encode(payload, key, algorithm="HS256")
    
    def decode_access_token(self, access_token):
        if isinstance(access_token, bytes):
            access_token = access_token.decode("ascii")
        if access_token.startswith("Bearer "):
            split = access_token.split("Bearer")
            access_token = split[1].strip()

        try:
            key = config.secret_key
            payload = jwt.decode(access_token, key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            error = "Access token expired. Please log in again."
            return error
        except jwt.InvalidTokenError:
            error = "Invalid token. Please log in again."
            return error
        
        user_dict = dict(
            user_email=payload["user_email"],
            user_role=payload["user_role"],
            token=access_token,
            expires_at=payload["exp"],
        )
        return user_dict
        
    def auth_login_reqparser(self):
        # constructs reqparser for auth_login api
        auth_reqparser = RequestParser(bundle_errors=True)
        auth_reqparser.add_argument(
            name="email", type=email(), location="form", required=True, nullable=False
        )
        auth_reqparser.add_argument(
            name="password", type=str, location="form", required=True, nullable=False
        )
        return auth_reqparser
    
    def get_token_expire_time(self):
        token_age_m = config.token_expire_minutes
        expires_in_seconds = token_age_m * 60
        return expires_in_seconds

    def create_auth_successful_response(self, token, status_code, message):
        # response = jsonify(
        #     status="success",
        #     message=message,
        #     access_token=token,
        #     token_type="bearer",
        #     expires_in=self.get_token_expire_time(),
        # )
        # response.status_code = status_code
        # response.headers["Cache-Control"] = "no-store"
        # response.headers["Pragma"] = "no-cache"
        response = {
            'status':'success',
            'message': message,
            'access_token': token,
            'token_type':'bearer',
            'expires_in':self.get_token_expire_time()
        }
        return response
    
    def process_login_request(self, email, password):
        user = self.users.find_one({"email": re.compile(email, re.IGNORECASE)})
        if not user or not check_password_hash(user['password'], password):
            abort(HTTPStatus.UNAUTHORIZED, "email or password does not match", status="fail")
        if user['role'] == 'Member':
            abort(HTTPStatus.UNAUTHORIZED, "members are not authorized", status="fail")

        access_token = self.encode_access_token(user)
        return self.create_auth_successful_response(
            token=access_token,
            status_code=HTTPStatus.OK,
            message="successfully logged in",
        )
            
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
                
        
    def users_change_maker_checker(self, target_email): 
        # TODO: complete maker-checker after implementing user passwords
        # for every create/update/delete user operation, check whether another admin has the made the same request
        # if have: proceed with the operation
        # else: submit 1st req to db, and wait for the second admin to make the same operation
        # db headers needed: target user_email, admin user_email requester, admin user_email approver, status (waiting approval/approved)
        
        
        return 

    def create(self, data): # TODO: add maker-checker
        user = data
        user.pop('_id', None)
        current_datetime = datetime.now().isoformat()
        user['date_joined'] = current_datetime # current local datetime in iso format
        user['password'] = generate_password_hash(user['password']) # hash password
        self.users.insert_one(user)

    def update(self, email, data): # TODO: add maker-checker
        user = data
        user.pop('_id', None) # mongodb objectid can't be changed
        user.pop('date_joined', None) # date_joined won't be changed
        user['password'] = generate_password_hash(user['password'])
        result = self.users.update_one({'email': email}, {'$set': data}, True)
        return result.raw_result
        
    def delete(self, email): # TODO: add maker-checker
        user = self.users.delete_one({'email': email })
        #return user.raw_result
    
DAO = UserDAO()

    
@ns.route('/user') # input parameter
class UsersList(Resource):
    # """GET all users, and POST a new user"""
    """GET all users"""
    @ns.doc('get_all_users')
    def get(self):  # input parameter
        """Get all users"""
        result = list((DAO.users.find()))
        res = {'result': result, 'response': "200"}
        return jsonify(res)

    # @ns.doc('create_a_user')
    # @ns.expect(user, validate=False)
    # def post(self):
    #     """Create a new user"""
    #     print(ns.payload)
    #     return DAO.create(ns.payload), 201
    
@ns.route('/auth/login') # input parameter
class AuthLogin(Resource):
    # """GET all users, and POST a new user"""
    """Get Bearer Token"""
    @ns.doc('auth_login')
    @ns.expect(DAO.auth_login_reqparser())
    def post(self):  # input parameter
        """Get Login Token"""
        req = DAO.auth_login_reqparser().parse_args()
        print(req)
        email = req.get('email')
        password = req.get('password')
        result = DAO.process_login_request(email, password)
        res = {'result': result, 'response': 200}
        return res
    
@ns.route('/auth/create_new_user') # input parameter
class CreateUser(Resource):
    """Create a new user via HTTP POST"""
    @ns.doc('create_a_user')
    @ns.expect(user, validate=False)
    def post(self):
        """Create a new user"""
        print(ns.payload)
        return DAO.create(ns.payload), 201

@ns.route('/auth/modify_user/<email>') # input parameter
@ns.param('email', 'The email of the user (str)')
@ns.response(404, 'User not found')
class ModifyUser(Resource):
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

@ns.route('/user/<email>') # input parameter
@ns.param('email', 'The email of the user (str)')
@ns.response(404, 'User not found')
class Users(Resource):
    # """Fetch a single user, update a user, or delete a user based on their email"""
    """Fetch a single user"""
    @ns.doc('get_a_user')
    def get(self, email): # input parameter
        """Fetch a user by email"""
        return DAO.get(email)
    
    # @ns.doc('delete_a_user')
    # def delete(self, email):
    #     """Delete a given user by its email"""
    #     DAO.delete(email)
    #     return "", 204

    # @ns.doc('update_a_user')
    # @ns.expect(user, validate=False)
    # def put(self, email):
    #     """Update a given user by its email"""
    #     return DAO.update(email, ns.payload)
    
@ns.route('/get_users_of_same_role/<role>') # input parameter
@ns.param('role', 'The role of the user (str)')
@ns.response(404, 'User not found')
class ManyUsers(Resource):
    @ns.doc('get_all_user_of_the_same_role')
    def get(self, role): # input parameter
        """Fetch all users that have the same role"""
        return DAO.get_all_same_role(role)