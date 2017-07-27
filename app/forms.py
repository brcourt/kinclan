from flask.ext.wtf import Form
from wtforms import TextField

from app import db
from app.models import User


class LoginValidator(object):
    def __init__(self, username, password):
        self.__username = username
        self.__password = password

    @property
    def is_valid(self):
        user = self.lookup_user
        if user is None:
            return False

        if user.password != self.__password:
            return False

        return True

    @property
    def lookup_user(self):
        return db.session.query(User).filter_by(email=self.__username).first()


class PostForm(Form):
    content = TextField('content')

class MessageForm(Form):
    content = TextField('content')
