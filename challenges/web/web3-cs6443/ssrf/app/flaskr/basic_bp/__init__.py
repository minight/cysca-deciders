from flask import Blueprint

app = Blueprint('app',
    __name__,
    template_folder='templates',
    static_folder='static')

from . import views
