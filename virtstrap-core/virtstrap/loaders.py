"""
virtstrap.loaders
-----------------

Loads commands from various locations. Currently only loads 
virtstrap.commands.*
"""

import os
import inspect
import pkg_resources
from virtstrap.log import logger
from virtstrap import commands
from virtstrap.utils import import_string

class CommandLoader(object):
    def __init__(self, collectors):
        # FIXME force the user of CommandLoader to give collectors
        self._collectors = collectors

    def load(self):
        """Collects all commands"""
        for collector in self._collectors:
            collected_commands = collector.collect()
            for command in collected_commands:
                commands.registry.register(command)

class Collector(object):
    def collect(self):
        raise NotImplementedError('Collector must define a collect method')

class ModuleCollectionMixin(object):
    def collect_commands_in_module(self, module):
        collected_commands = []
        for name, variable in module.__dict__.iteritems():
            if inspect.isclass(variable):
                bases = inspect.getmro(variable)
                if commands.Command in bases:
                    collected_commands.append(variable)
        return collected_commands


class BuiltinCommandCollector(Collector, ModuleCollectionMixin):
    def __init__(self, location):
        self._location = location

    def collect(self):
        commands = import_string(self._location)
        builtin_command_dir = os.path.abspath(
                os.path.dirname(commands.__file__))

        import_template = '%s.%s' % (commands.__name__, '%s')

        builtin_command_files = os.listdir(builtin_command_dir)

        collected_commands = []

        for filename in builtin_command_files:
            if filename.endswith('.py') and not filename == '__init__.py':
                # Load the file. That's all that should be necessary
                module_name = filename[:-3]
                import_path_string = import_template % module_name
                try:
                    command_module = import_string(import_path_string)
                except ImportError:
                    logger.exception('Failed to collect builtin command '
                        'module "%s"' % filename)
                else:
                    collected_commands.extend(
                            self.collect_commands_in_module(command_module))
        return collected_commands


class PluginCommandCollector(Collector, ModuleCollectionMixin):
    def __init__(self, entry_point):
        self._entry_point = entry_point

    def collect(self):
        collected_commands = []
        for plugin in pkg_resources.iter_entry_points(self._entry_point):
            collected_commands.extend(self.collect_commands_in_module(plugin))
        return collected_commands
