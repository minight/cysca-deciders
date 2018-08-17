from flask import Blueprint

app = Blueprint('demo',
    __name__,
    template_folder='templates',
    static_folder='static')

from . import views
