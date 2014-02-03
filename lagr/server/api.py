import flask
from .manager import LogManager
from .channels import manager
from .queue import PullQueueHandler

api_bp = flask.Blueprint('api', __name__)

@api_bp.route('/v1/', methods=['POST'])
def v1():
    PullQueueHandler(queue_name='logs-queue').inject(flask.request.get_json())
    # LogManager().process_log(flask.request.get_json())
    # manager.send(flask.request.data)

    return 'OK'

