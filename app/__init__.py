from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)

app.config.from_object('app.config')
socketio = SocketIO(app)


login_manager = LoginManager(app)
login_manager.session_protection = "strong"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)


from app import views, models
