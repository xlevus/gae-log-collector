import flask
import os
from decorators import login_required

from .channels import manager

static_folder = os.path.join(os.path.split(__file__)[0], 'static')
templates_folder = os.path.join(os.path.split(__file__)[0], 'templates')


ui_bp = flask.Blueprint('ui', __name__, static_folder=static_folder, template_folder=templates_folder)

@login_required
@ui_bp.route('/')
def index():
    return flask.render_template(
        'index.html',
        token=manager.new())

