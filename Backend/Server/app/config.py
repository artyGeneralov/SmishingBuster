class Config:
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///default.db'

class DevelopmentConfig(Config):
    DEBUG = True

class ProducitonConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql://user:password@server/db"
