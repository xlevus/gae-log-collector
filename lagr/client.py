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
            'trigger': [],

        }

        if hasattr(r, 'traceback'):
            dd.update({
                'traceback': r.traceback
            })

        if hasattr(r, 'exception'):
            dd.update({
                'exception': r.exception
            })

        if hasattr(r, 'trigger'):
                dd['trigger'] = r.trigger.serialize(r)
        return dd

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
            data=json.dumps(record))

        response = urllib2.urlopen(req)
        print "Response: %s" % response.status


class LagrGAEHandler(LagrHandler):
    def __init__(self, application=None, host=None, proto=None, url=None, level=logging.NOTSET, async=True, deadline=30):
        self.async = async
        self.deadline = deadline

        super(LagrGAEHandler, self).__init__(application=application, host=host, proto=proto, url=url, level=level)

    def make_request(self, data):
        url = '%(proto)s://%(host)s/%(url)s' % {
                'proto': self.proto,
                'host': self.host,
                'url': self.url
            }

        print "------- MAKING REQUEST to url=%s" % url

        from google.appengine.ext import ndb
        ctx = ndb.get_context()

        future = ctx.urlfetch(
            url=url,
            payload=json.dumps(data),
            method='POST',
            headers={'Content-Type':'application/json'},
            deadline=self.deadline)

        if self.async:
            return future

        return future.get_result()

