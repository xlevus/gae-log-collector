from werkzeug.utils import import_string


class LogManager(object):
    """ This class has the responsibility to handle the log server-side (so plays with caches etc. etc. """

    @classmethod
    def process_log(cls, log):
        import pdb; pdb.set_trace()

        for plugin in log['plugins']:
            key = plugin.pop("key")
            plugin_id = plugin.pop("__id__")
            plugin.update({'id': plugin_id})
            klass = import_string(key)
            plugin_obj = klass(**plugin)

            # Plugin execution
            plugin_obj.execute()
