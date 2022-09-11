from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from bson.objectid import ObjectId
from common.db import *
import re


db = mongo['abc_books']
ns = Namespace('Borrow', description='APIs for Borrowing/Returning of books')

borrow = ns.model('Borrow', {
    'book_id': fields.String(required=False, description='The unique id of the book'),
    'user_email': fields.String(required=True, description='The email of the borrowing user'),
})


@ns.route('/borrow') # input parameter
class Borrow(Resource):
    @ns.doc('borrow_a_book')
    @ns.expect(borrow)
    def post(self):
        """Borrow a book"""
        book_id = ns.payload['book_id']
        user_email = ns.payload['user_email']
        
        # check if book is available to borrow
        book = db['books'].find_one(ObjectId(book_id))
        if book['borrowing_availability_status'] == False:
            return jsonify({'result': "failed, this book is not available for borrowing", 'response': 200})
            
        # push borrowed book into user's books_on_borrow list in the db
        res1 = db['users'].update_one({'email':re.compile(user_email, re.IGNORECASE)}, {'$push': {'books_on_borrow': book_id}})
        print(res1.raw_result)
        
        # change book last_borrower and borrowing_availability_status in the db
        res2 = db['books'].update_one({'_id': ObjectId(book_id)}, {'$set': {'borrowing_availability_status': False, 'last_borrower': user_email}})
        print(res2.raw_result)
        
        return jsonify({'result': "success", 'response': 200})
    
@ns.route('/return') # input parameter
class Return(Resource):
    @ns.doc('return_a_book')
    @ns.expect(borrow, validate=False)
    def post(self):
        """Return a book"""
        book_id = ns.payload['book_id']
        user_email = ns.payload['user_email']
        
        # remove borrowed book from user's books_on_borrow list in the db
        res1 = db['users'].update_one({'email':re.compile(user_email, re.IGNORECASE)}, {'$pull': {'books_on_borrow': book_id}})
        print(res1.raw_result)
        
        # change book borrowing_availability_status in the db
        res2 = db['books'].update_one({'_id': ObjectId(book_id)}, {'$set': {'borrowing_availability_status': True}})
        print(res2.raw_result)
        
        
        return jsonify({'result': "success", 'response': 200})
    
        
        
        
        
        