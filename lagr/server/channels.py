import time
import random

import flask
from google.appengine.ext import ndb
from google.appengine.api import channel

channel_bp = flask.Blueprint('channels', __name__)


class ChannelClient(ndb.Model):
    bit = ndb.BooleanProperty(default=True)


class ChannelManager(object):
    def new(self):
        client_id = '%s_%s' % (time.time(), random.random())
        return channel.create_channel(client_id)

    def add(self, client_id):
        if client_id:
            ChannelClient(id=client_id).put()

    def remove(self, client_id):
        if client_id:
            ndb.Key(id=client_id).delete()

    def clients(self):
        for key in ChannelClient.query().iter(keys_only=True):
            yield key.id()

    def send(self, message):
        for client_id in self.clients():
            channel.send_message(client_id, message)


manager = ChannelManager()


@channel_bp.route('/_ah/channel/connected/', methods=['POST'])
def channel_connected():
    client_id = flask.request.form.get('from')
    manager.add(client_id)
    return 'OK'


@channel_bp.route('/_ah/channel/disconnected/', methods=['POST'])
def channel_disconnected():
    client_id = flask.request.form.get('from')
    manager.remove(client_id)
    return 'OK'

