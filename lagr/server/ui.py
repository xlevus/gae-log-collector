import flask
import os
import sys
import traceback
import logging
from lagr.client import LagrGAEHandler
from lagr.server import plugins

from .channels import manager

static_folder = os.path.join(os.path.split(__file__)[0], 'static')
templates_folder = os.path.join(os.path.split(__file__)[0], 'templates')

APP = "Test app"
HOST = "localhost:8080"
URL = 'lagr/api/v1'
PROTO = 'http'

ui_bp = flask.Blueprint('ui', __name__, static_folder=static_folder, template_folder=templates_folder)

@ui_bp.route('/')
def index():
    return flask.render_template('index.html', token=manager.new())


logger = logging.getLogger(__name__)
logger2 = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.addHandler(LagrGAEHandler(application=APP, host=HOST, proto=PROTO, url=URL, level=logging.DEBUG,async=False))



logger2.setLevel(logging.DEBUG)
logger2.addHandler(LagrGAEHandler(application="Test App 2", host=HOST, proto=PROTO, url=URL, level=logging.DEBUG,async=False))

@ui_bp.route('/test_view')
def test_view():
    trigger = plugins.HideBelowThreshold(threshold=5)
    alert = plugins.HipChatAlert(room='python-temp')
    expiration = plugins.Expiration(hours=24)
    email = plugins.EmailAlert()
    trigger.add(alert)
    trigger.add(expiration)
    trigger.add(email)
    try:
        1/0
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for i in range(20):

            logger.info("Info message - should be shown on realtime monitor", extra={
                'trigger': trigger,
                'exception': e.message,
                'traceback': traceback.format_tb(exc_traceback, 20)
                })
            logger2.info("Info message - should be shown on realtime monitor", extra={
                'trigger': trigger,
                'exception': e.message,
                'traceback': traceback.format_tb(exc_traceback, 20)
                })
    return "Sent."

