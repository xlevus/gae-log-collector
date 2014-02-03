from google.appengine.api.taskqueue import TransientError
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError
from google.appengine.api import taskqueue
from flask import views
import logging
import flask

logger = logging.getLogger(__name__)


class PullQueueHandler(object):

    class UnableToExtractTasks(Exception):

        def __init__(self, retries):
            self.message = 'unable to extract tasks from the queue in %d tries' % retries

        def __str__(self):
            return self.message

    def __init__(self, queue_name):
        self._queue_name = queue_name
        self._q = taskqueue.Queue(name=self._queue_name)

    def inject(self, payload):
        if payload is not None:
            if type in (list, tuple) is False:
                raise TypeError('%s.inject takes a list or a tuple in input, got a %s' % (self.__class__.__name__, type(payload)))
            else:
                 map(lambda x: self._q.add(taskqueue.Task(payload=x, method="PULL")), payload)
        else:
            raise ValueError('%s.inject cannot take an empty payload' % self.__class__.__name__)

    def lease(self, retries=3):

        tries = 0
        while tries < retries:
            try:
                return self._q.lease_tasks(3, 5)
            except (TransientError, DeadlineExceededError), ex:
                logger.critical("unable to lease tasks. Error was: %s" % ex.message)

        if tries == retries:
            logger.critical('unable to extract tasks from the queue in %d tries' % retries)
            raise self.UnableToExtractTasks(retries)

queue_monitor_bp = flask.Blueprint('queue', __name__)

class QueueMonitor(flask.views.MethodView):

    def get(self):
        pqh = PullQueueHandler(queue_name='logs-queue')
        try:
            tasks = pqh.lease()
        except PullQueueHandler.UnableToExtractTasks:
            # Not logging, the queue itself logs this.
            pass
        return "OK"

queue_monitor_bp.add_url_rule('/QueueMonitor/', view_func=QueueMonitor.as_view('cron'))