class Config(object):
    def __init__(self):
        self.mongo_uri = "mongodb://localhost:27017/abc_books"
        self.port = "5010"
        self.secret_key = "secret_key"
        self.token_expire_minutes = 5