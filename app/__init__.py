from flask import Flask, Blueprint, request
import flask_login
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import flask.globals as flask_global

app = Flask(__name__)
db = SQLAlchemy(app)

app.config.from_object('app.config')
socketio = SocketIO(app)


login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

from app.auth_page import *
from app.calendar import *
from app.home import *
from app.members import *
from app.messages import *
from app.pictures import *
from app.profile import *


app.register_blueprint(auth_page)
app.register_blueprint(calendar)
app.register_blueprint(home)
app.register_blueprint(members)
app.register_blueprint(messages)
app.register_blueprint(pictures)
app.register_blueprint(profile)


# @login_manager.user_loader
# def load_user(user_id):
#     blueprint = flask_global.current_app.blueprints[request.blueprint]
#
#     if hasattr(blueprint, load_user):
#         return blueprint.load_user(user_id)
#
#     return None


from app import models

print app.url_map
