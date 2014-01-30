import flask

lagr_server = flask.Flask(__name__)
from .api import api_bp
lagr_server.register_blueprint(api_bp, url_prefix='/lagr/api')

from .ui import ui_bp
lagr_server.register_blueprint(ui_bp)

from .channels import channel_bp
lagr_server.register_blueprint(channel_bp)

from .taskqueues import LogDeletionQueue
from .taskqueues import log_deletion_bp
lagr_server.register_blueprint(log_deletion_bp, url_prefix='/_q')
