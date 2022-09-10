from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from bson.objectid import ObjectId
# from .db import get_db
# from flask import current_app, g
# from werkzeug.local import LocalProxy
# from flask_pymongo import PyMongo
# from pymongo import MongoClient
from common.db import *
ns = Namespace('Book', description='API for Book management')

book = ns.model('Book', {
    '_id': fields.String(required=False, description='The unique id of the book that will be converted into an ObjectId'),
    'title': fields.String(required=True, description="The title of the book"),
    'description': fields.String(required=False, description='The description of the book'),
    'genre': fields.String(required=False, description='The genre of the book'),
    'author': fields.String(required=False, description='The author of the book'),
    'year_published': fields.Integer(required=False, description='The year the book is published'),
    'borrowing_availability_status': fields.Boolean(required=False, description='The borrowing availability status of the book'),
    'last_borrower': fields.String(required=False, description='The last borrower of the book')
})

db = mongo['abc_books']

class BookDAO(object):
    def __init__(self):
        self.counter = 0
        self.books = db['books']

    def get(self, title):
        book = self.books.find_one({"title": title})
        return book
        ns.abort(404, "Book {} doesn't exist".format(id))
        
    def get_all_same_title(self, title):
        book = self.books.find({"title": title})
        result = list(book)
        res = {'result': result, 'response': "200"}
        return jsonify(res)
        ns.abort(404, "Book {} doesn't exist".format(id))

    def create(self, data):
        book = data
        book.pop('_id', None)
        self.books.insert_one(book)

    def update(self, title, data):
        result = self.books.update_one({'title': title}, data, True)
        return result.raw_result
        
    def delete(self, title):
        book = self.books.delete_one({'title': title })
        return book.raw_result
    

DAO = BookDAO()

@ns.route('/book') # input parameter
class BooksList(Resource):
    """GET all books, and POST a new book"""
    @ns.doc('get_all_modules')
    #@ns.marshal_list_with(book)
    def get(self):  # input parameter
        """Get all books"""
        result = list((DAO.books.find()))
        res = {'result': result, 'response': "200"}
        return jsonify(res)

    @ns.doc('create_a_book')
    @ns.expect(book)
    #@ns.marshal_with(book, code=201)
    def post(self):
        """Create a new book"""
        return DAO.create(ns.payload), 201

@ns.route('/book/<title>') # input parameter
@ns.param('title', 'The title of the book (str)')
@ns.response(404, 'Book not found')
class Books(Resource):
    """Fetch a single book, update a book, or delete a book"""
    @ns.doc('get_a_book')
    #@ns.marshal_list_with(book)
    def get(self, title): # input parameter
        """Fetch a book by its title"""
        return DAO.get(title)
    
    
    
    @ns.doc('delete_a_book')
    def delete(self, title):
        """Delete a given book by its title"""
        DAO.delete(title)
        return "", 204

    @ns.doc('update_a_book')
    @ns.expect(book)
    #@ns.marshal_with(book)
    def put(self, title):
        """Update a given book by its title"""
        return DAO.update(title, ns.payload)
    
@ns.route('/many_books/<title>') # input parameter
@ns.param('title', 'The title of the book (str)')
@ns.response(404, 'Book not found')
class AllBooks(Resource):
    @ns.doc('get_all_book_of_the_same_title')
    #@ns.marshal_list_with(book)
    def get(self, title): # input parameter
        """Fetch all books that have the same title"""
        return DAO.get_all_same_title(title)




