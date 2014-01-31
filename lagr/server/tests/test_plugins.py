import mock
from flask.ext.testing import TestCase
import flask
from lagr.server import plugins
from lagr.server.models import Log
from google.appengine.ext import testbed
from google.appengine.api import mail
from google.appengine.api import memcache
from lagr.server.plugins import requests


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


class HideBelowThresholdTests(BaseTests):

    def setUp(self):
        super(HideBelowThresholdTests, self).setUp()
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

    def test_add(self):
        """ Tests HideBelowThreshold.add method. """
        hb = plugins.HideBelowThreshold(id="some-id")
        hc = plugins.HipChatAlert(room='test')
        hb.add(hc)

        self.assertTrue(hc in hb.plugins)
        self.assertEqual(len(hb.plugins), 1)

    @mock.patch.object(memcache, 'get')
    def test_verify(self, fake_get):
        """ Tests HideBelowThreshold.veify method. """
        fake_get.return_value = 9
        ID = 'some-memcache-key'
        hbt = plugins.HideBelowThreshold(id=ID)
        hc = plugins.HipChatAlert(room='room')
        hbt.add(hc)
        with mock.patch.object(plugins.HipChatAlert, 'execute') as fake_ex:
            hbt.verify(self.log)
        fake_ex.assert_called_with(self.log)



class HipChatAlertPluginTests(BaseTests):

    def setUp(self):
        super(HipChatAlertPluginTests, self).setUp()
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

    def test_format(self):
        """ Tests _format method. """

        log = {
            'application': "Test application",
            'time': "10:00:00 1/1/2014",
            'message': "Test message",
            'traceback': 'some message',
            'exception': 'fake excpetion'
        }

        hc = plugins.HipChatAlert(room='python-temp')
        result = hc._format(log)
        expected = hc.TEMPLATE % log
        self.assertEqual(result, expected)

    def test_serialize(self):
        """ Tests serialize method. """

        hc = plugins.HipChatAlert(room='python-temp')
        result =  hc.serialize()
        expected = {
            'key': "%s.%s" % (hc.__module__, hc.__class__.__name__),
            'room': "python-temp"
        }

        self.assertEqual(result, expected)

    def test_execute_ok(self):
        """ Tests execute method successes. """
        with mock.patch.object(requests, 'post') as fake_post:
            fake_post.return_value = mock.MagicMock(status_code=200, content="OK")
            hc = plugins.HipChatAlert(room='python-temp')
            hc.execute(self.log)

            self.assertTrue(fake_post.called)

    def test_execute_fail(self):
        """ Tests execute method failures. """
        with mock.patch.object(requests, 'post') as fake_post:
            fake_post.return_value = mock.MagicMock(status_code=403, content="Error")
            hc = plugins.HipChatAlert(room='python-temp')
            with self.assertRaises(Exception):
                hc.execute(self.log)


class ExpirationTest(BaseTests):

    def setUp(self):
        super(ExpirationTest, self).setUp()
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

    def test_serialize(self):
        """ Tests Expiration.serialize method. """
        expiration = plugins.Expiration(hours=1)
        result =  expiration.serialize()

        expected = {
            'key': "%s.%s" % (expiration.__module__, expiration.__class__.__name__),
            'hours': 1
        }

        self.assertEqual(result, expected)

    def test_execute(self):
        """ Tests Expiration.execute method. """
        expiration = plugins.Expiration(hours=1)
        expiration.execute(self.log)
        self.assertEqual(Log.query().count(),1)

class EmailAlertPluginTests(BaseTests):

    def setUp(self):
        super(EmailAlertPluginTests, self).setUp()
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
                        "email_ids": ['a@b.com'],
                        "key": "lagr.server.plugins.EmailAlert"
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

    def test_format(self):
        """ Tests _format method. """

        log = {
            'application': "Test application",
            'time': "10:00:00 1/1/2014",
            'message': "Test message",
            'traceback': 'some message',
            'exception': 'fake excpetion'
        }

        email = plugins.EmailAlert(email_ids=['a@b.com'])
        result = email._format(log)
        expected = email.TEMPLATE % log
        self.assertEqual(result, expected)

    def test_serialize(self):
        """ Tests serialize method. """

        email = plugins.EmailAlert(email_ids=['a@b.com'])
        result =  email.serialize()
        expected = {
            'key': "%s.%s" % (email.__module__, email.__class__.__name__),
            'email_ids': ['a@b.com']
        }

        self.assertEqual(result, expected)

    @mock.patch.object(mail.EmailMessage, 'send')
    def test_execute_ok(self, send):
        """ Tests execute method successes. """

        mail = plugins.EmailAlert(email_ids=['a@b.com'])
        mail.execute(self.log)
        send.assert_once_called_with()

