from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os

db = SQLAlchemy()
class ConfigClass(object):
    # Flask settings
    # DEBUG = True
    SECRET_KEY = "wegkjawetu23871rhkskjhgbakjerhb"
    SQLALCHEMY_DATABASE_URI         = 'postgresql+psycopg2://adminisbestusername:hunter2isbestpassword@db:5432/magicdatabase'
    SQLALCHEMY_ECHO                 = True
    FLAG2 = "flag{flag_this_isnt_a_flag_but_youre_making_progress2}"

def register_models(app):
    with app.app_context():
        db.init_app(app)

def register_blueprints(app):
    from .demo import app as demo
    app.register_blueprint(demo)

def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')

    register_models(app)
    register_blueprints(app)

    return app

