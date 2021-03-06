try:
    from google.appengine.api import memcache
except ImportError:
    pass

from .models import Log

import requests
import logging

logger = logging.getLogger(__name__)

HIPCHAT_API_TOKEN = '329c9b499ffb8d087a8cd6988e8084'


class Serializable(object):

    def serialize(self):
        raise NotImplementedError("To be implemented by serializable classes")


class Trigger(object):

    def verify(self, log):
        raise NotImplementedError('Trigger logic has to be implemented by concrete classes')

    def serialize(self, log):
        raise NotImplementedError("To be implemented by serializable classes")


class HideBelowThreshold(Trigger):

    def __init__(self, id=None, threshold=10, plugins=None):
        self.id = id
        self.threshold = threshold
        self.plugins = plugins

    def serialize(self, log):
        if self.id == None:
            self.id = str(hash("%s.%s" % (log.filename, log.lineno)))
        index = self.__module__.split(".").index('lagr')
        path = self.__module__.split(".", index)[1]
        key = "%s.%s" % (path, self.__class__.__name__)

        return {
            'id': self.id,
            'key': key,
            'threshold': self.threshold,
            'plugins': map(lambda x: x.serialize(), self.plugins)
        }

    def add(self, plugin):
        """
        :param plugin: the plugin we want to add to the list. Type is verified;
        """
        assert issubclass(plugin.__class__, Plugin)
        if self.plugins is not None:
            self.plugins.append(plugin)
        else:
            self.plugins = [plugin]

    def verify(self, log):
        existing = memcache.get(key=self.id) or 0

        if existing == 0:
            memcache.add(key=self.id, value=1, time=1)
        else:
            memcache.incr(self.id)
            existing += 1

            if existing == self.threshold:
                map(lambda x: x.execute(log), self.plugins)
                memcache.delete(key=self.id)



class Plugin(Serializable):
    """ Base plugin class """

    def execute(self, log):
        raise NotImplementedError('Must be implemented by the subclasses')

    def base_info(self):
        # This is needed because in client apps the path of the plugins will be different from the one on the server.
        index = self.__module__.split(".").index('lagr')
        path = self.__module__.split(".", index)[1]
        key = "%s.%s" % (path, self.__class__.__name__)
        return {
            'key': key,
        }


class HipChatAlert(Plugin):

    TEMPLATE = """
    <table>
        <tr>
            <td><strong>Application</strong>: %(application)s</td>
        </tr>
        <tr>
            <td><strong>Timestamp</strong>: %(time)s</td>
        </tr>
        <tr>
            <td><strong>Message</strong>: %(message)s</td>
        </tr>
        <tr>
            <td><strong>Traceback</strong>: %(traceback)s</td>
        </tr>
        <tr>
            <td><strong>Exception</strong>: %(exception)s</td>
        </tr>

    </table>
    """

    def __init__(self, hipchat_token, room):
        self.room = room
        self.token = hipchat_token

    def _format(self, log):

        return self.TEMPLATE % {
            'application': log['application'],
            'time': log['time'],
            'message': log['message'],
            'traceback': ''.join(log['traceback']),
            'exception': log['exception'],
        }

    def serialize(self):

        b_info = super(HipChatAlert, self).base_info()

        b_info.update({
                'room': self.room
            })

        return b_info

    def execute(self, log):
        """ Reacts to the trigger. """
        logger.info("<<< Executing %s" % self.__class__.__name__)
        url = "%s%s?auth_token=%s" % ('https://api.hipchat.com/v1/', 'rooms/message', self.token)
        data = {
            'room_id': self.room,
            'from': "Lagr Monitor",
            'message': self._format(log),
            'message_format': "html",
            'notify': 1,
            'color': "red",
        }
        response = requests.post(url, data=data)
        if (response.status_code != 200):
            raise Exception(response.content)


class Expiration(Plugin):
    """ This plugin stores the log triggering the handler with a specific duration. When it expires, the record is
    deleted. """

    def __init__(self, hours=0):
        """
        :param hours: number of hours the log should stay in the datastore. After that, it will automatically destroyed.
        """

        self.hours = hours

    def serialize(self):

        b_info = self.base_info()
        b_info.update({
            'hours': self.hours
        })

        return b_info

    def execute(self, log):
        self.log = log
        Log.create(log, self.hours)
