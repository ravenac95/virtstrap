"""
virtstrap.baseplugin
--------------------

The base plugin for virtstrap.
"""
from functools import wraps
from virtstrap.log import logger

class Plugin(object):
    name = None
    command = None

    def __init__(self):
        self.options = None
        self.logger = logger

    def execute(self, event, options, **kwargs):
        """Wraps the user defined run method in the proper environment"""
        self.options = options
        self.logger.debug('Running "%s" plugin for "%s" command' % 
                (self.name, self.command))
        return_code = 0
        try:
            self.run(event, options, **kwargs)
        except SystemExit, e:
            return_code = e.code
        except:
            self.logger.exception('An error occured executing plugin "%s"' %
                    self.__class__.__name__)
            return_code = 2
        finally:
            self.options = None
        return return_code

    def run(self, event, options, **kwargs):
        raise NotImplementedError('Please implement a run method '
                'for this plugin')

class GeneratedPlugin(Plugin):
    def __init__(self, name, command, events, runner):
        super(GeneratedPlugin, self).__init__()
        self.name = name
        self.command = command
        self.events = events
        self._runner = runner

    def run(self, event, options, **kwargs):
        self._runner(event, options, **kwargs)

def create(command, events):
    def decorator(f):
        return GeneratedPlugin(f.__name__, command, events, f)
    return decorator
