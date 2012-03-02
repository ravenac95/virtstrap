"""
virtstrap.runner
----------------

The main runner for the virtstrap application. If you wish to call
virtstrap from within your program. The simplest way would be to use
the runner and feed it the arguments.
"""

import sys
import os
from optparse import OptionParser
from virtstrap import constants
from virtstrap import commands
from virtstrap.log import logger, setup_logger
from virtstrap.loaders import CommandLoader, BuiltinCommandCollector
from virtstrap.registry import CommandDoesNotExist, CommandRegistry

EXIT_FAIL = 1
EXIT_OK = 0

def create_loader(*args):
    collector = BuiltinCommandCollector('virtstrap.commands')
    return CommandLoader(collectors=[collector])

def create_registry(*args):
    return CommandRegistry()

class VirtstrapRunner(object):
    """Routes command line to different commands"""
    def __init__(self, registry_factory=create_registry, 
            loader_factory=create_loader):
        self._loader_factory = loader_factory
        self._loader = None
        
        # Set registry settings
        self._registry_factory = registry_factory
        self._registry = None

        self._args = []

    def set_registry(self, registry):
        self._registry = registry

    def set_loader(self, loader):
        self._loader = loader

    def set_args(self, args):
        self._args = args

    @property
    def registry(self):
        """Lazily loads the registry"""
        registry = self._registry
        if not registry:
            registry = self._registry_factory(self._args)
            self._registry = registry
        return registry

    @property
    def loader(self):
        """Lazily loads the command loader"""
        loader = self._loader
        if not loader:
            loader = self._loader_factory(self._args)
            self._loader = loader
        return loader

    def main(self, args=None):
        """Handles execution through command line interface"""
        # Load all of the available commands
        self.set_args(args)
        self.load_commands()
        parser = self.create_parser()
        if not args:
            args = sys.argv[1:]
        cli_args = parser.parse_args(args=args)
        self.handle_global_options(cli_args)
        command = cli_args.command
        # Run the command
        try:
            exit_code = self.run_command(command, cli_args)
        except CommandDoesNotExist:
            exit_code = EXIT_FAIL
            logger.debug('Unknown command "%s"' % command)
            parser.error('"%s" is not a vstrap command. (use "vstrap help" '
                    'to see a list of commands)' % command)
        finally:
            self.close_context()
        if exit_code == EXIT_OK:
            # TODO actually delete the correct log file
            if os.path.exists(constants.LOG_FILE): 
                os.remove(constants.LOG_FILE)
        return exit_code

    def handle_global_options(self, cli_args):
        setup_logger(cli_args.verbosity, 
                cli_args.no_colored_output, cli_args.log_file)

    def load_commands(self):
        """Tell loader to load commands"""
        commands.registry = self.registry
        command_loader = self.loader
        command_loader.load()

    def list_commands(self):
        return self.registry.list_commands()

    def close_context(self):
        """Removes the registry from commands.registry"""
        self._registry = None
        commands.registry = None

    def create_parser(self):
        return self.registry.create_cli_parser()

    def run_command(self, name, cli_args, **kwargs):
        """Load command from virtstrap.commands"""
        logger.debug('Command "%s" chosen' % name)
        return self.registry.run(name, cli_args, **kwargs)

def main(args=None):
    runner = VirtstrapRunner()
    exit = runner.main(args=args)
    if exit:
        sys.exit(exit)
