import mock
from flask.ext.testing import TestCase
import flask
import logging
from lagr import client
from lagr import plugins
import urllib2

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

    def test_alert(self):
        """ """
        # Simulates an alert that triggers hipchat notification to bingo room if at least 10 logs enter the system in
        # one second

        req = urllib2.Request(
            '%(proto)s://%(host)s/%(url)s' % {
                'proto': "http",
                'host': "localhost:8080",
                'url': "lagr/api/v1/"
            },
            headers={'Content-Type':'application/json'},
            data=[])

        with mock.patch("lagr.client.urllib2.Request") as fake_request:
            with mock.patch.object(client.urllib2, "urlopen") as fake_open:

                fake_request.return_value = req
                fake_open.return_value = True
                alert = plugins.Alert(10, "HipChat", ['bingo',])
                logger = logging.getLogger(__name__)
                handler = client.LagrHandler(level=logging.DEBUG)
                logger.addHandler(handler)
                logger.info("Test log", extra={'alerts': [alert,]})
                fake_open.assert_called_with(req)