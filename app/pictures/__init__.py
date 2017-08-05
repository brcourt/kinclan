from flask import Blueprint

pictures = Blueprint('pictures', __name__, template_folder='templates')

import views
