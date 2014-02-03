import flask
import json
import mock
import os
import datetime
from google.appengine.ext import testbed
from flask.ext.testing import TestCase
from lagr.server.queue import PullQueueHandler
from google.appengine.api import taskqueue


class BaseTests(TestCase):

    def create_app(self):
        app = flask.Flask(__name__)
        app.config.update({
            'APPLICATION': "Test application",
            'PROTO': 'http',
            'HOST': 'localhost:8080',
            'URL': 'lagr/api/v1/'
        })

        return app

    def setUp(self):
        super(BaseTests, self).setUp()
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub(root_path=os.path.abspath(os.path.join(__file__, '../../../..')))

    def tearDown(self):
        super(BaseTests, self).tearDown()
        self.testbed.deactivate()


class QueueTests(BaseTests):

    def test_injection(self):

        payload = json.dumps({
            'status': True,
            'message': "This is the message"
        })
        with mock.patch.object(taskqueue.Queue, 'add') as fake_add:
            pqh = PullQueueHandler(queue_name='logs-queue')
            pqh.inject(payload=[payload])
