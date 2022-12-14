# from common.db import mongo

from flask_restx import Api, Namespace

from .book_endpoint import ns as book_ns
from .user_endpoint import ns as user_ns
from .borrow_endpoint import ns as borrow_ns

authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}
api = Api(
    title='ABC Book Club Web Services',
    version='1.0',
    description='List of APIs for ABC Book Club',
    doc='/docs',
    authorizations=authorizations
    # All API metadatas
)
url_prefix = "/api/v1"
# initialize namespaces to api
api.add_namespace(book_ns, path=url_prefix)
api.add_namespace(user_ns, path=url_prefix)
api.add_namespace(borrow_ns, path=url_prefix)

