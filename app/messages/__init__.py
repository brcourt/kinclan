from flask import Blueprint

messages = Blueprint('messages', __name__, template_folder='templates')

import views
