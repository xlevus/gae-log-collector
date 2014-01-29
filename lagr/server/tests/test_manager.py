from flask.ext.testing import TestCase
import flask
from google.appengine.ext import testbed
from lagr.server.manager import LogManager
from lagr.server.plugins import HideBelowThreshold
import mock


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
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()


class ManagerTests(BaseTests):

    def setUp(self):
        super(ManagerTests, self).setUp()
        self.log = {
            "msg_args": [],
            "line_number": 48,
            "func_name": "test_view",
            "module": "ui",
            "level_number": 20,
            "message": "Info message - should be shown on realtime monitor",
            "exception": "integer division or modulo by zero",
            "level": "INFO",
            "trigger": {
                "threshold": 5,
                "id": "6961289232517810357",
                "key": "lagr.server.plugins.HideBelowThreshold",
                "plugins": [
                    {
                        "room": "python-temp",
                        "key": "lagr.server.plugins.HipChatAlert"
                    }
                ]
            },
            "traceback": [
                "  File \"/Users/bruno.ripa/dev/gamesys_ve/gae-log-collector/lagr/server/ui.py\", line 42, in test_view\n    1/0\n"
            ],
            "filename": "ui.py",
            "application": "Test app",
            "raw_msg": "Info message - should be shown on realtime monitor",
            "time": "14:35:50 29/01/2014"
        }

    def test_process(self):
        """ Tests LogManager.process_log method. """
        lm = LogManager()

        with mock.patch.object(HideBelowThreshold, "verify") as fake_v:
            lm.process_log(self.log)

        fake_v.assert_called_with(self.log)