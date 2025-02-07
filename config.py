import os
from dotenv import load_dotenv


load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql:///financemanager')

class ProductionConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(Config): 
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False