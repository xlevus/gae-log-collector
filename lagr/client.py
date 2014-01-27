import json
import logging
import flask
import datetime
import urllib2

HOST = 'localhost:8080'
PROTO = 'http'
URL = 'lagr/api/v1/'

class LagrHandler(logging.Handler):
    def __init__(self, application=None, host=None, proto=None, url=None, level=logging.NOTSET):
        if flask.has_request_context():
            self.host = flask.current_app.config['HOST']
            self.proto = flask.current_app.config['PROTO']
            self.url = flask.current_app.config['URL']
            self.application = flask.current_app.config['APPLICATION']
        else:
            self.host = host
            self.proto = proto
            self.url = url
            self.application = application

        super(LagrHandler, self).__init__(level)

    def format_record(self, r):
        dd = {
            'application': self.application,
            'message': self.format(r),

            'time': datetime.datetime.fromtimestamp(int(r.created)).strftime("%H:%M%:%S %d/%m/%Y"),

            'raw_msg': r.msg,
            'msg_args': r.args,

            'level': r.levelname,
            'level_number': r.levelno,

            'filename': r.filename,
            'line_number': r.lineno,

            'module': r.module,
            'func_name': r.funcName,
            'plugins': []
        }

        for index, plugin in enumerate(r.alerts):
            dd['plugins'].append(plugin.serialize(index, r))

        return json.dumps(dd)

    def handleError(self, record):
        print record

    def emit(self, record):
        record = self.format_record(record)
        self.make_request(record)

    def make_request(self, record):
        url = '%(proto)s://%(host)s/%(url)s' % {
                'proto': self.proto,
                'host': self.host,
                'url': self.url
            }
        req = urllib2.Request(
            url,
            headers={'Content-Type':'application/json'},
            data=record)
        response = urllib2.urlopen(req)


class LagrGAEHandler(LagrHandler):
    def __init__(self, level=logging.NOTSET, async=True, deadline=30):
        self.async = async
        self.deadline = deadline

        super(LagrGAEHandler, self).__init__(level)

    def make_request(self, data):
        url = '%(proto)s://%(host)s/%(url)s' % {
                'proto': self.proto,
                'host': self.host,
                'url': self.url
            }

        from google.appengine.ext import ndb
        ctx = ndb.get_context()

        future = ctx.urlfetch(
            url=url,
            payload = json.dumps(data),
            method='POST',
            headers={'Content-Type':'application/json'},
            deadline=self.deadline)

        if self.async:
            return future

        return future.get_result()

