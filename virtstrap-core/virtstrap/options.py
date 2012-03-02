"""
virtstrap.options
-----------------

Defines various tools for dealing with command line options.
"""

import sys
import pkg_resources
from argparse import ArgumentParser
from virtstrap import constants
from virtstrap.exceptions import *
from virtstrap.log import logger

# Sorry pip! Stole this from you
try:
    virtstrap_dist = pkg_resources.get_distribution('virtstrap')
    version = '%s from %s (python %s)' % (
        virtstrap_dist, virtstrap_dist.location, sys.version[:3])
except pkg_resources.DistributionNotFound:
    version=None

class CLIList(list):
    """Special list type that is used for command line interface lists"""
    def __str__(self):
        self_as_strings = map(lambda a: str(a), self)
        return ','.join(self_as_strings)

def list_str(string):
    return CLIList(map(lambda a: a.strip(), string.split(',')))

def create_base_parser():
    global_parser = create_global_parser()
    project_parser = create_project_parser()
    parser = ArgumentParser(
        add_help=False,
        parents=[global_parser, project_parser],
    )
    return parser

def create_global_parser():
    """This is the basic parser that all parsers will inherit."""
    parser = ArgumentParser(
        add_help=False
    )
    global_group = parser.add_argument_group('global options')
    global_group.add_argument('--version', action='version', version=version)
    global_group.add_argument('-v', '--verbosity', dest='verbosity', 
            action='store', type=int, default=2,
            metavar='LVL',
            help='set verbosity level. [0, 1, 2, 3]')
    global_group.add_argument('-l', '--log', dest='log_file', metavar='FILE',
            action='store', default=constants.LOG_FILE,
            help='log file')
    global_group.add_argument('--no-colored-output', dest='no_colored_output',
            action='store_true', default=False,
            help='do not use output colors')
    return parser

def create_project_parser():
    parser = ArgumentParser(
        add_help=False
    )
    project_group = parser.add_argument_group('project options')
    project_group.add_argument('--virtstrap-dir', dest='virtstrap_dir',
            action='store', default=constants.VIRTSTRAP_DIR,
            metavar='DIR',
            help='the directory for the virtual environment')
    project_group.add_argument('--profiles', dest='profiles',
            action='store', help='specify a profile', type=list_str,
            default='development')
    project_group.add_argument('--project-dir', dest='project_dir',
            metavar='PROJECT_DIR',
            action='store', help='specify project directory')
    project_group.add_argument('--config-file', dest='config_file',
            action='store', default=constants.VE_FILENAME,
            help='specify a configuration file')
    return parser

def global_options_to_args(options):
    # FIXME Rename uses of this function
    return base_options_to_args(options)

def base_options_to_args(options):
    option_map = ( 
        ('config_file', '--config-file'),
        ('log_file', '--log'),
        ('profiles', '--profiles'),
        ('project_dir', '--project-dir'),
        ('verbosity', '--verbosity'),
        ('virtstrap_dir', '--virtstrap-dir'),
    )
    args = []
    for option_var, option_flag in option_map:
        value = getattr(options, option_var, None)
        if not value:
            continue
        args.append('%s=%s' % (option_flag, value))
    return args

def parser_from_commands(commands):
    """Creates a parser from all the passed in commands

    It does this by using multiple parents to create a brand new subparser
    """
    base_parser = create_base_parser()
    top_parser = ArgumentParser(
        parents=[base_parser]
    )
    subparsers = top_parser.add_subparsers(help='Commands',
            metavar='command', dest='command')
    for command_name, command in commands:
        command_parser = command.parser
        if not isinstance(command_parser, ArgumentParser):
            logger.error('%s does not define parser with argparse. '
                    'It will not be included in commands' % command_name)
        subparsers.add_parser(command_name,
                help=command.description,
                add_help=False,
                parents=[base_parser, command.parser]
            )
    return top_parser
