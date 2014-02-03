from google.appengine.api import taskqueue


class PullQueueHandler(object):

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
