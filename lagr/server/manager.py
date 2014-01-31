from werkzeug.utils import import_string
import logging
import json

logger = logging.getLogger(__name__)

class LogManager(object):
    """ This class has the responsibility to handle the log server-side (so plays with caches etc. etc. """

    def process_log(self, log):
        trigger = log.get('trigger', None)
        if trigger is not None:
            plugins = trigger.pop('plugins')

            trigger_key = trigger.pop('key')
            trigger_obj = import_string(trigger_key)(**trigger)

            for plugin in plugins:
                plugin_key = plugin.pop("key")
                klass = import_string(plugin_key)
                logger.debug("Plugin: %s Klass: %s" % (plugin, klass))
                plugin_obj = klass(**plugin)
                trigger_obj.add(plugin_obj)

            logger.info("--------------- VERIFYING")
            # Plugin execution
            trigger_obj.verify(log)

