"""
virtstrap_system.runner
-----------------------

The system wide script runner. The need for separation between the system wide
runner and the project's local runner is to provide support for different
python versions while still using all of the same code. 
"""
import re
import sys
from virtstrap.argparse import ArgumentParser
from virtstrap.loaders import *
from virtstrap.project import *
from virtstrap.options import create_project_parser
from virtstrap_system.loaders import ProjectCommandCollector
from virtstrap.runner import VirtstrapRunner
from virtstrap import commands
from virtstrap import constants
from virtstrap.log import logger
from virtstrap.registry import CommandDoesNotExist

VS_DIR_OPTION = '--virtstrap-dir'
PROJ_DIR_OPTION = '--project-dir'

EXIT_OK = 0
EXIT_FAIL = 2

class ProjectFactory(commands.ProjectMixin):
    def __call__(self, args):
        project_args = self.gather_project_args(args)

        parser = self.project_parser()
        options = parser.parse_args(project_args)
        try:
            project = self.load_project(options)
        except NoProjectFound:
            return None
        return project

    def project_parser(self):
        return create_project_parser()

    def gather_project_args(self, args):
        project_args = []
        options = ['virtstrap-dir', 'profiles', 'project-dir', 'config-file']
        joined_options = '|'.join(options)
        option_regex = '^--(%s)=' % joined_options
        matcher = re.compile(option_regex)
        for arg in args:
            match = matcher.match(arg)
            if match:
                project_args.append(arg)
        return project_args

NONE_OBJ = object()

def create_loader(args, project):
    main_collector = BuiltinCollector('virtstrap_system.commands')
    plugin_collector = PluginCollector('virtstrap_system.plugins')
    project_collector = ProjectCommandCollector(args, project)
    return CommandLoader(collectors=[main_collector, plugin_collector, 
        project_collector])

class VirtstrapSystemWideRunner(VirtstrapRunner):
    def __init__(self, project_factory=None, **kwargs):
        kwargs['loader_factory'] = create_loader
        super(VirtstrapSystemWideRunner, self).__init__(**kwargs)
        self._project = NONE_OBJ
        self._project_factory = project_factory or ProjectFactory()

    def main(self, args=None):
        """Handles execution through command line interface"""
        # This is so you can see virtstrap starting in the log file
        logger.debug('------------------- vstrap starting -------------------')
        # Load all of the available commands
        if not args:
            args = sys.argv[1:]
        self.set_args(args)
        self.load_commands()
        parser = self.create_parser()
        # Get the arguments minus the command name
        raw_command_args = args[1:] 
        # Parse the known args
        cli_args, remaining = parser.parse_known_args(args=args)
        self.handle_global_options(cli_args)
        command = cli_args.command
        # Run the command
        exit_code = 0
        try:
            exit_code = self.run_command(command, cli_args, 
                    project=self.project, raw_args=raw_command_args)
        except CommandDoesNotExist:
            exit_code = EXIT_FAIL
            logger.debug('Unknown command "%s"' % command)
            parser.error('"%s" is not a vstrap command. (use "vstrap help" '
                    'to see a list of commands)' % command)
        except SystemExit, e:
            if e.code == 0:
                exit_code = EXIT_OK
            else:
                logger.error("virtstrap did not finish it's"
                        " task correctly check the log. for more information")
        finally:
            self.close_context()
        if exit_code == EXIT_OK:
            # TODO actually delete the correct log file
            if os.path.exists(constants.LOG_FILE): 
                os.remove(constants.LOG_FILE)
        return exit_code

    @property
    def project(self):
        project = self._project
        if project is NONE_OBJ:
            project = self._project_factory(self._args)
            self._project = project
        return project

    def set_project(self, project):
        self._project = project

    @property
    def loader(self):
        """Lazily loads the command loader"""
        loader = self._loader
        if not loader:
            loader = self._loader_factory(self._args, self.project)
            self._loader = loader
        return loader

def main(args=None):
    runner = VirtstrapSystemWideRunner()
    exit = runner.main(args=args)
    if exit:
        sys.exit(exit)
