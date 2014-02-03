import flask

lagr_server = flask.Flask(__name__)
lagr_server.config.update({'HIPCHAT_API_TOKEN': '329c9b499ffb8d087a8cd6988e8084'})

from .api import api_bp
lagr_server.register_blueprint(api_bp, url_prefix='/lagr/api')

from .ui import ui_bp
lagr_server.register_blueprint(ui_bp)

from .channels import channel_bp
lagr_server.register_blueprint(channel_bp)

from .taskqueues import LogDeletionQueue
from .taskqueues import log_deletion_bp
lagr_server.register_blueprint(log_deletion_bp, url_prefix='/_q')

from queue import queue_monitor_bp
lagr_server.register_blueprint(queue_monitor_bp, url_prefix='/_q')

print lagr_server.url_map