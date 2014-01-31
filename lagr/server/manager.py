from werkzeug.utils import import_string
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class LogManager(object):
    """ This class has the responsibility to handle the log server-side (so plays with caches etc. etc. """

    def process_log(self, log):
        hipchat_token = current_app.config.get("HIPCHAT_API_TOKEN")
        trigger = log.get('trigger', None)
        if trigger is not None:
            plugins = trigger.pop('plugins')

            trigger_key = trigger.pop('key')
            trigger_obj = import_string(trigger_key)(**trigger)

            for plugin in plugins:
                plugin_key = plugin.pop("key")
                klass = import_string(plugin_key)
                plugin_obj = klass(hipchat_token=hipchat_token, **plugin)
                trigger_obj.add(plugin_obj)

            # Plugin execution
            trigger_obj.verify(log)

