# from common.db import mongo

from flask_restx import Api, Namespace

from .book_endpoint import ns as book_ns
from .user_endpoint import ns as user_ns
from .borrow_endpoint import ns as borrow_ns

api = Api(
    title='ABC Book Club Web Services',
    version='1.0',
    description='List of APIs for ABC Book Club',
    doc='/docs'
    # All API metadatas
)

# initialize namespaces to api
api.add_namespace(book_ns)
api.add_namespace(user_ns)
api.add_namespace(borrow_ns)

