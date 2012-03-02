"""
virtstrap.registry
------------------

Defines a command and plugin registry. This allows you to register many 
commands in a number of locations.
"""

from virtstrap.options import parser_from_commands

class CommandAlreadyExists(Exception):
    pass

class CommandDoesNotExist(Exception):
    pass

class CommandRegistry(object):
    def __init__(self):
        self._registered_commands = {}

    def register(self, command, name=None):
        """Registers a commandobject using name"""
        name = name or command.name
        current_command = self._registered_commands.get(name, None)
        if not current_command:
            self._registered_commands[name] = command
        else:
            raise CommandAlreadyExists('Command names must be unique.')

    def retrieve(self, name):
        return self._registered_commands.get(name, None)

    def commands_iter(self):
        return iter(sorted(self._registered_commands.iteritems()))
    
    def run(self, name, options, **kwargs):
        """Runs command with name"""
        command_class = self.retrieve(name)
        if not command_class:
            raise CommandDoesNotExist('Command "%s" does not exist' % name)
        command = command_class()
        return command.execute(options, **kwargs)

    def list_commands(self):
        """Return a list of command names"""
        return map(lambda a: a[0], self.commands_iter())

    def print_command_help(self):
        """Display all the commands and their descriptions"""
        print('')
        print('Commands available:')
        for command_name, command in self.commands_iter():
            print('  %s: %s' % (command_name, command.description))

    def create_cli_parser(self):
        """Creates a command line interface parser for all commands"""
        return parser_from_commands(self.commands_iter())


