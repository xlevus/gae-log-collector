from google.appengine.ext import ndb
from google.appengine.api import memcache

import logging

logger = logging.getLogger(__name__)

class Plugin(object):
    """ All the plugins need to implement a `serialize` method. """

    def __init__(self, id=None):
        self.id = None

    def serialize(self, idx, log):
        raise NotImplementedError('Must be implemented by the subclasses')

    def execute(self):
        raise NotImplementedError('Must be implemented by the subclasses')

    def base_info(self):

        return {
            'key': "%s.%s" % (self.__class__.__module__, self.__class__.__name__),
            '__id__': self.id,
        }



class Alert(Plugin):

    def __init__(self, id=None, threshold="10", system=None, recipients=[]):
        """
        :param threshold: the number of logs per second that will trigger the action
        :param systems: the syste to be used to notify user (eg: HipChat, E-Mail, ..)
        :param recipients: contextual target for notifications. In case of HipChat that's a list of room numbers,
        in case of e-mail it's a list of recipients.
        """
        self.id = id
        self.threshold = threshold
        self.system = system
        self.recipients = recipients
        super(Alert, self).__init__(id)

    def serialize(self, idx, log):

        if not self.id:
            self.id = hash("%s.%s.%s" % (idx, log.filename, log.lineno))

        b_info = self.base_info()

        b_info.update({

                'threshold': self.threshold,
                'system': self.system,
                'recipients': self.recipients
            })

        return b_info

    def execute(self):
        counter = 1
        if self.id not in memcache:
            memcache.add(self.id,1,1)
        else:
            counter = memcache.get(self.id)

        if counter >= self.threshold:
            logger.critical('Triggering handler for %s plugin' % self.__class__.__name__)





class Expiration(Plugin):

    def __init__(self, id=None, hours=0):
        """
        :param hours: number of hours the log should stay in the datastore. After that, it will automatically destroyed.
        """

        self.hours = 0

        super(Expiration, self).__init__(id)


    def serialize(self, idx, log):

        if not self.id:
            self.id = hash("%s.%s.%s" % (idx, log.filename, log.lineno))

        b_info = self.base_info()
        b_info.update({

                'expiration': self.hours
            })

        return b_info
