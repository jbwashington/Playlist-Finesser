APPLICATION_NAME = 'FinesseFM'
DEBUG = True
SECRET_KEY = 'mysecretkey'
DATABASE_URI_DEV = 'sqlite:///finesse.db'

class Development(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///finesse.db'

class Testing(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgres://user:pass@test/my_database'


class Production(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgres://user:pass@prod/my_database'
