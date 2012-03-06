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
from virtstrap import plugins
from virtstrap.utils import import_string

class CommandLoader(object):
    def __init__(self, collectors):
        # FIXME force the user of CommandLoader to give collectors
        self._collectors = collectors

    def load(self):
        """Collects all commands"""
        registry = commands.registry
        for collector in self._collectors:
            collected_commands, collected_plugins = collector.collect()
            for command in collected_commands:
                registry.register_command(command)
            for plugin in collected_plugins:
                registry.register_plugin(plugin)

class Collector(object):
    def collect(self):
        raise NotImplementedError('Collector must define a collect method')

class ModuleCollectionMixin(object):
    def collect_in_module(self, module):
        collected_commands = []
        collected_plugins = []
        for name, variable in module.__dict__.iteritems():
            # Is the variable a class
            if inspect.isclass(variable):
                bases = inspect.getmro(variable)
                # is it a command class?
                if commands.Command in bases:
                    collected_commands.append(variable)
            # Is the variable a plugin instance
            elif isinstance(variable, plugins.Plugin):
                collected_plugins.append(variable)
        return collected_commands, collected_plugins

class BuiltinCollector(Collector, ModuleCollectionMixin):
    def __init__(self, location):
        self._location = location

    def collect(self):
        commands = import_string(self._location)
        builtin_command_dir = os.path.abspath(
                os.path.dirname(commands.__file__))

        import_template = '%s.%s' % (commands.__name__, '%s')

        builtin_command_files = os.listdir(builtin_command_dir)

        collected_commands = []
        collected_plugins = []

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
                    command_list, plugin_list = self.collect_in_module(
                            command_module)
                    collected_commands.extend(command_list)
                    collected_plugins.extend(plugin_list)
        return collected_commands, collected_plugins


class PluginCollector(Collector, ModuleCollectionMixin):
    def __init__(self, entry_point):
        self._entry_point = entry_point

    def collect(self):
        collected_commands = []
        collected_plugins = []
        for plugin_entry in pkg_resources.iter_entry_points(self._entry_point):
            plugin = plugin_entry.load()
            command_list, plugin_list = self.collect_in_module(plugin)
            collected_commands.extend(command_list)
            collected_plugins.extend(plugin_list)
        return collected_commands, collected_plugins
