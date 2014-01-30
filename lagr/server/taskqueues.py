import flask
import datetime
import logging
from lagr.server.models import Log


from iwishared.gae.flask_taskqueue import PushQueueHandler

logger = logging.getLogger(__name__)

log_deletion_bp = flask.Blueprint('log_deletion', __name__)

class LogDeletionQueue(PushQueueHandler):
    queue_name = 'loose-fb-intents'
    blueprint = log_deletion_bp
    auto_register = True

    def run(self):
        q = Log.query().filter(Log.expiration<=datetime.datetime.utcnow())
        q.map(lambda x: x.delete())
        return "OK"

