import sys
import json
from virtstrap.loaders import Collector
from virtstrap import commands
from virtstrap import constants
from virtstrap.log import logger

def call_project_command(project, command_name, command_args, output_errors=False,
        **subprocess_options):
    virtstrap_bin = constants.PROJECT_VIRTSTRAP_BIN_NAME
    args = [command_name]
    args.extend(command_args)
    try:
        return_data = project.call_bin(virtstrap_bin, args,
                **subprocess_options)
    except OSError:
        logger.debug('Error executing virtstrap local command')
        command_bin_path = project.bin_path(virtstrap_bin)
        command_list = [command_bin_path]
        command_list.extend(args)
        command_string = ' '.join(command_list)
        logger.debug('Command called: %s' % command_string)
        sys.exit(2)

class WrappedProjectCommand(commands.Command):
    """A special command that wraps a project command"""
    def execute(self, registry, options, project=None, raw_args=None, **kwargs):
        self.registry = registry
        self.options = options
        return_code = 0
        try:
            call_project_command(project, self.name, raw_args)
        except OSError:
            # Assume that the project command will display it's own errors
            self.logger.debug('Error running "%s" command' % self.name)
            return_code = 2
        finally:
            self.options = None
            self.registry = None
        return return_code

class ProjectCommandCollector(Collector):
    def __init__(self, args=None, project=None):
        self._args = args or []
        self._project = project

    def collect(self):
        project = self._project
        collected_commands = []
        if project:
            virtstrap_bin = constants.PROJECT_VIRTSTRAP_BIN_NAME
            try:
                json_data = project.call_bin(virtstrap_bin, ['commands',
                    '--as-json'], collect_stdout=True)
            except OSError:
                logger.error('Found a possible project directory at %s'
                        ' but it was not configured correctly.' % 
                        project.path())
                return collected_commands, []
            if json_data:
                commands_json = json.loads(json_data)
                command_dicts = commands_json['commands']
                for command_dict in command_dicts:
                    command = self.make_local_project_command(
                            command_dict['name'], 
                            command_dict['description'])
                    collected_commands.append(command)
        # Collectors need to return commands and plugins but this collector
        # does not collect plugins so return an empty list
        return collected_commands, []

    def make_local_project_command(self, command_name,
            command_description):
        class LocalProjectCommand(WrappedProjectCommand):
            name = command_name
            description = command_description
        return LocalProjectCommand
