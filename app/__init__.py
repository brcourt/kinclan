from flask import Flask, Blueprint, request
import flask_login
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import flask.globals as flask_global

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config.from_object('app.config')
socketio = SocketIO(app)


login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'


from app.auth import *
from app.calendar import *
from app.chat import *
from app.home import *
from app.members import *
from app.messages import *
from app.pictures import *
from app.profile import *


app.register_blueprint(auth)
app.register_blueprint(calendar)
app.register_blueprint(chat)
app.register_blueprint(home)
app.register_blueprint(members)
app.register_blueprint(messages)
app.register_blueprint(pictures)
app.register_blueprint(profile)


from app import models

print app.url_map
