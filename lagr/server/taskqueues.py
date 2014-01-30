import datetime
from lagr.server.models import Log
import logging
import cPickle as pickle
import flask
from flask.views import View

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

logger = logging.getLogger(__name__)

log_deletion_bp = flask.Blueprint('log_deletion', __name__)



class PushQueueMeta(type):
    def __new__(meta, name, bases, attrs):
        klass = super(PushQueueMeta, meta).__new__(meta, name, bases, attrs)
        if klass.queue_name and klass.auto_register:
            klass.register(klass.blueprint)
        return klass


class PushQueueHandler(View):
    """ """
    __metaclass__ = PushQueueMeta
    methods = ['POST']

    auto_register = True
    queue_name = None
    blueprint = None

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def dispatch_request(self):
        queue_name = flask.request.headers.get('X-AppEngine-QueueName')
        if not queue_name:
            flask.abort(403, "This must be run from a taskqueue")
        args, kwargs = pickle.loads(flask.request.data)

        try:
            resp = self.run(*args, **kwargs)
            if isinstance(resp, ndb.Future):
                resp.get_result()
        except Exception:
            logger.warning("Task failed. Attempt %s",
                flask.request.headers.get('X-AppEngine-TaskRetryCount', -1),
                exc_info=True)
            return "FAILURE", 500

        return "OK"

    @classmethod
    def _pop_queue_args(cls, **kwargs):
        queue = {
            'eta': kwargs.pop('_eta', None),
            'name': kwargs.pop('_name', None),
            'target': kwargs.pop('_target', None),
            'transactional': kwargs.pop('_transactional', None),
        }
        return queue, kwargs

    @classmethod
    def queue(cls, *args, **kwargs):
        """
        :param _eta: `datetime.datetime` ETA of the task.
        :param _name: `str` name of the task.
        :param _target: Instance or backend to run the task against.
        :param _transactional: Queue the task on transaction success.

        :param *args: Forwarded to ``run`` method.
        :param **kwargs: Forwarded to ``run`` method.
        """
        queue_args, kwargs = cls._pop_queue_args(**kwargs)

        payload = pickle.dumps((args, kwargs))

        taskqueue.add(
            url=cls._url(),
            queue_name=cls.queue_name,
            payload=payload,

            **queue_args
        )

    @classmethod
    def _url(cls):
        if isinstance(cls.blueprint, flask.Blueprint):
            return flask.url_for('%s.%s' % (cls.blueprint.name, cls.__name__))
        else:
            return flask.url_for('%s' % (cls.__name__))

    @classmethod
    def register(cls, app, url_prefix=''):
        cls.blueprint = app
        cls_name = cls.__name__
        app.add_url_rule('%s/%s/' % (url_prefix, cls_name),
                         view_func=cls.as_view(cls_name))


class LogDeletionQueue(PushQueueHandler):
    queue_name = 'loose-fb-intents'
    blueprint = log_deletion_bp
    auto_register = True

    def run(self):
        q = Log.query().filter(Log.expiration<=datetime.datetime.utcnow())
        q.map(lambda x: x.delete())
        return "OK"

