from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os

db = SQLAlchemy()

def get_current_ip():
    with open("/etc/hosts") as f:
        lines = f.readlines()
    return lines[-1].split('\t')[0]


class ConfigClass(object):
    # Flask settings
    # DEBUG = True
    SECRET_KEY                      = 'fuckyouandyoursecretkey'
    SQLALCHEMY_DATABASE_URI         = 'postgresql+psycopg2://adminisbestusername:hunter2isbestpassword@db:5432/magicdatabase'
    #SQLALCHEMY_DATABASE_URI         = 'sqlite:////tmp/tmp.sqlite'
    SQLALCHEMY_ECHO                 = True
    FLAG1 = os.getenv("FLAG", "flag{this_isnt_a_flag_but_youre_making_progress}")
    SSRF_HOST = os.getenv("SSRF_HOST", "ssrf")
    SECRET_KEY = "awerglllaliwuhgoiaweuhto8q237598oq27y3toiuq23hteoiuawh"
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "FLAG{jdusNrj8Fm8jnW84zcWZS9IJUqp7X2OgFIaZMrVID2ArAXXvp_EgLlE4RXu38mIogMijb_3gwAY}")

    THIS_IP = get_current_ip()

def register_models(app):
    from .basic_bp import models

    with app.app_context():
        db.init_app(app)
    #    db.drop_all()
        db.create_all()

        models.populate()

def register_blueprints(app):
    from .basic_bp import app as basic_bp
    app.register_blueprint(basic_bp)

def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')

    register_models(app)
    register_blueprints(app)

    return app

