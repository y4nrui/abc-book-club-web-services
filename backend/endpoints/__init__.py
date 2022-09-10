# from common.db import mongo

from flask_restx import Api, Namespace

from .book_endpoint import ns as book_ns

api = Api(
    title='ABC Book Web Services',
    version='1.0',
    description='List of APIs for ABC Book',
    # All API metadatas
)

api.add_namespace(book_ns)


