from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from bson.objectid import ObjectId
# from .db import get_db
# from flask import current_app, g
# from werkzeug.local import LocalProxy
# from flask_pymongo import PyMongo
# from pymongo import MongoClient
from common.db import *
from endpoints.user_endpoint import UserDAO
import re

db = mongo['abc_books']
ns = Namespace('Book', description='APIs for Book management')

book = ns.model('Book', {
    '_id': fields.String(required=False, description='The unique id of the book (auto-generated)'),
    'title': fields.String(required=True, description="The title of the book"),
    'description': fields.String(required=False, description='The description of the book'),
    'genre': fields.String(required=False, description='The genre of the book'),
    'author': fields.String(required=False, description='The author of the book'),
    'year_published': fields.Integer(required=False, description='The year the book is published'),
    'borrowing_availability_status': fields.Boolean(required=False, description='The borrowing availability status of the book'),
    'last_borrower': fields.String(required=False, description="The last borrower of the book, represented by the borrower's email")
})


class BookDAO(object):
    def __init__(self):
        self.books = db['books']
        
    def bearer_header_parser(self):
        parser = ns.parser()
        parser.add_argument(name='Authorization', location='headers', type=str)
        return parser

    def get(self, title):
        book = self.books.find_one({"title": re.compile(title, re.IGNORECASE)})
        #print(book)
        return jsonify(book)
        ns.abort(404, "Book {} doesn't exist".format(id))
        
    def get_all_same_title(self, title):
        book = self.books.find({"title": re.compile(title, re.IGNORECASE)})
        result = list(book)
        res = {'result': result, 'response': "200"}
        return jsonify(res)
        ns.abort(404, "Book {} doesn't exist".format(id))

    def create(self, data):
        book = data
        book.pop('_id', None)
        self.books.insert_one(book)

    def update(self, title, data):
        book = data
        book.pop('_id', None)
        result = self.books.update_one({'title': title}, {'$set': data}, True)
        return result.raw_result
        
    def delete(self, title):
        book = self.books.delete_one({'title': title })
        #return book.raw_result
    
DAO = BookDAO()
UserDAO = UserDAO()

@ns.route('/book') # input parameter
class BooksList(Resource):
    """GET all books, and POST a new book"""
    @ns.doc('get_all_books')
    #@ns.marshal_list_with(book)
    def get(self):  # input parameter
        """Get all books"""
        result = list((DAO.books.find()))
        res = {'result': result, 'response': "200"}
        return jsonify(res)

    # @ns.doc('create_a_book')
    # @ns.expect(book)
    # #@ns.marshal_with(book, code=201)
    # def post(self):
    #     """Create a new book"""
    #     return DAO.create(ns.payload), 201

@ns.route('/auth/create_new_book') # input parameter
@ns.doc(security="Bearer",parser=DAO.bearer_header_parser())
class CreateBook(Resource):
    """Create a new book"""
    @ns.doc('create_a_book')
    @ns.expect(book)
    def post(self):
        """Create a new book (requires Editor or Admin authorization token)"""
        access_token = DAO.bearer_header_parser().parse_args()['Authorization']
        result = UserDAO.check_access_token(access_token, must_be_admin=False)
        if isinstance(result, str):
            return jsonify({'message': result, 'response': 200})
        DAO.create(ns.payload), 201
        return jsonify({'message': "new book has been successfully added", 'response': 201})

@ns.route('/book/<title>') # input parameter
@ns.param('title', 'The title of the book (str)')
@ns.response(404, 'Book not found')
class Books(Resource):
    # """Fetch a single book, update a book, or delete a book"""
    """Fetch a single book"""
    @ns.doc('get_a_book')
    #@ns.marshal_list_with(book)
    def get(self, title): # input parameter
        """Fetch a book by its title"""
        return DAO.get(title)

@ns.route('/auth/modify_book/<title>') # input parameter
@ns.param('title', 'The title of the book (str)')
@ns.response(404, 'Book not found')
@ns.doc(security="Bearer",parser=DAO.bearer_header_parser())
class ModifyBook(Resource):
    """Update a book, or delete a book"""
    @ns.doc('delete_a_book')
    def delete(self, title):
        """Delete a given book by its title (requires Editor or Admin authorization token)"""
        access_token = DAO.bearer_header_parser().parse_args()['Authorization']
        result = UserDAO.check_access_token(access_token, must_be_admin=False)
        if isinstance(result, str):
            return jsonify({'message': result, 'response': 200})
        DAO.delete(title)
        return jsonify({'message': "book has been successfully deleted", 'response': 204})

    @ns.doc('update_a_book')
    @ns.expect(book, validate=False)
    #@ns.marshal_with(book)
    def put(self, title):
        """Update a given book by its title (requires Editor or Admin authorization token)"""
        access_token = DAO.bearer_header_parser().parse_args()['Authorization']
        result = UserDAO.check_access_token(access_token, must_be_admin=False)
        if isinstance(result, str):
            return jsonify({'message': result, 'response': 200})
        DAO.update(title, ns.payload)
        return jsonify({'message': "book's details has been successfully updated", 'response': 200})
    
    
    
@ns.route('/get_books_of_same_title/<title>') # input parameter
@ns.param('title', 'The title of the book (str)')
@ns.response(404, 'Book not found')
class ManyBooks(Resource):
    @ns.doc('get_all_book_of_the_same_title')
    #@ns.marshal_list_with(book)
    def get(self, title): # input parameter
        """Fetch all books that have the same title"""
        return DAO.get_all_same_title(title)

@ns.route('/get_book_by_id/<id>') # input parameter
@ns.param('id', 'The id of the book')
class GetBookByID(Resource):
    @ns.doc('get_book_by_id')
    #@ns.marshal_list_with(book)
    def get(self, id): # input parameter
        """Fetch a book with the id"""
        #book = DAO.books.find_one({'_id': ObjectId(id)})
        book = DAO.books.find_one(ObjectId(id))
        #print(book['borrowing_availability_status'])
        return jsonify(book)
    
    # @ns.doc('update_book_genre_by_id')
    # @ns.expect(book, validate=False)
    # #@ns.marshal_list_with(book)
    # def put(self, id): # input parameter
    #     """Update genre of book with the id"""
    #     #book = DAO.books.find_one({'_id': ObjectId(id)})
    #     result = DAO.books.update_one({'_id': ObjectId(id)}, {'$set': {'genre': ns.payload['genre']}}, True)
    #     #print(result.raw_result)
    #     return result.raw_result



