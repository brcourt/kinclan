from flask import Blueprint

members = Blueprint('members', __name__, template_folder='templates')

import views
