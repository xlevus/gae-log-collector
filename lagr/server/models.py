from google.appengine.ext import ndb
import datetime


class Log(ndb.Model):

    created = ndb.DateTimeProperty(auto_now_add=True)
    exception = ndb.StringProperty(required=True)
    application = ndb.StringProperty(required=True)
    expiration = ndb.DateTimeProperty(required=True)
    message = ndb.StringProperty(required=True)
    log = ndb.JsonProperty(required=True)

    @classmethod
    def create(cls, log, duration=24):
        """
        :param log: the dict-based log info
        """
        # 14:16:34 28/01/2014
        expiration = datetime.datetime.strptime(log['time'], "%H:%M:%S %d/%m/%Y") + datetime.timedelta(hours=duration)
        cls(exception=log['exception'], application=log['application'], message=log['message'], expiration=expiration, log=log).put()

