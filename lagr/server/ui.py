import flask
import os
import logging
from lagr.client import LagrGAEHandler
from lagr import plugins

from .channels import manager

static_folder = os.path.join(os.path.split(__file__)[0], 'static')
templates_folder = os.path.join(os.path.split(__file__)[0], 'templates')


ui_bp = flask.Blueprint('ui', __name__, static_folder=static_folder, template_folder=templates_folder)

@ui_bp.route('/')
def index():
    return flask.render_template(
        'index.html',
        token=manager.new())


logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.addHandler(LagrGAEHandler(logging.DEBUG,async=True))


@ui_bp.route('/test_view')
def test_view():
    alert = plugins.Alert(system='HipChat', recipients='bingo')
    logger.info("Info message", extra={'alerts': [alert,]})
    return "Sent."
