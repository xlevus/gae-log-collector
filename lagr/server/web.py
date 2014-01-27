import flask

lagr_server = flask.Flask(__name__)
lagr_server.config.update({"APPLICATION": "Bingo"})
from .api import api_bp
lagr_server.register_blueprint(api_bp, url_prefix='/lagr/api')

from .ui import ui_bp
lagr_server.register_blueprint(ui_bp)

from .channels import channel_bp
lagr_server.register_blueprint(channel_bp)

