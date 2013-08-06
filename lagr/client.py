import json
import logging

HOST = 'localhost:8080'
PROTO = 'https'


class LagrHandler(logging.Handler):
    def format_record(self, r):
        return json.dumps({
            'message': self.format(r),

            'time': r.created,

            'raw_msg': r.msg,
            'msg_args': r.args,

            'level': r.levelname,
            'level_number': r.levelno,

            'filename': r.filename,
            'line_number': r.lineno,

            'module': r.module,
            'func_name': r.funcName,
        })

    def handleError(self, record):
        print record

    def emit(self, record):
        record = self.format_record(record)
        self.make_request(record)

    def make_request(self, data):
        import urllib2
        req = urllib2.Request(
            'http://localhost:8080/lagr/api/v1/',
            headers={'Content-Type':'application/json'},
            data=data)
        urllib2.urlopen(req)


class LagrGAEHandler(LagrHandler):
    def __init__(self, level=logging.NOTSET, async=True, deadline=30):
        self.async = async
        self.deadline = deadline

        super(LagrGAEHandler, self).__init__(level)

    def make_request(self, url, record):
        from google.appengine.ext import ndb
        ctx = ndb.get_context()

        future = ctx.urlfetch(
            url=url,
            payload = json.dumps(record),
            method='POST',
            headers={'Content-Type':'application/json'},
            deadline=self.deadline)

        if self.async:
            return future

        return future.get_result()

