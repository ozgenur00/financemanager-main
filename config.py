import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://dfumjnnp:Bd4UsUlodu6KrHnaZj99_NRU7jFWiSZU@kala.db.elephantsql.com/dfumjnnp'

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://dfumjnnp:Bd4UsUlodu6KrHnaZj99_NRU7jFWiSZU@kala.db.elephantsql.com/dfumjnnp'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory SQLite database for testing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
