import flask

from .channels import manager

api_bp = flask.Blueprint('api', __name__)

@api_bp.route('/v1/', methods=['POST'])
def v1():
    try:
        data = flask.request.get_json()
        manager.send(flask.request.data)
    except ValueError:
        return 'ERR'
    return 'OK'

