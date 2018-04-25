import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'sqlite.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'A secret development key.'
