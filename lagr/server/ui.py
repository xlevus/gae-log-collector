import flask

from .channels import manager

ui_bp = flask.Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    return flask.render_template(
        'ui.html',
        token=manager.new())

