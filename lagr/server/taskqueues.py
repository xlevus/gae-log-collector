from datetime import datetime, timedelta
import flask
import logging

from google.appengine.ext import ndb

from iwishared.gae.flask_taskqueue import PushQueueHandler

logger = logging.getLogger(__name__)

payment_recovery_bp = flask.Blueprint('payment_recovery', __name__)

class LogDeletionQueue(PushQueueHandler):
    queue_name = 'loose-fb-intents'
    blueprint = payment_recovery_bp

    def run(self, intent):
        at = Graph.get_access_token(
            app_id = intent.app_id,
            secret = flask.current_app.config.get('APP_IDS', {}).get('app_secret'))

        g = Graph(at)

        _, fb_id = intent.player.user_id.rsplit("|", 1)
        resp = g.get('/%s/payment_transactions' % fb_id, request_id=intent.key.id())

        if resp and resp.get('data'):
            for row in resp['data']: