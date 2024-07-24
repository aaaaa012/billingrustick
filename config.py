import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://anish_rustick:anish_rustick%401234567@localhost/rustick_final'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
