"""
virtstrap.project
-----------------

This module contains all the abstractions for dealing with a Project. 
Using this object simplifies creating commands that are used to manage
the project.
"""

import os
from virtstrap import constants
from virtstrap.config import VirtstrapConfig
from virtstrap.utils import call_subprocess

VIRTSTRAP_DIR = constants.VIRTSTRAP_DIR

class Project(object):
    @classmethod
    def load(cls, options):
        """Creates a project and loads it's configuration immediately"""
        project = cls()
        project.load_settings(options)
        return project

    def __init__(self):
        self._options = None
        self._config = None
    
    def load_settings(self, options):
        # Check if project directory is specified
        project_dir = getattr(options, 'project_dir', None)
        if not project_dir:
            project_dir = self._find_project_dir()
        project_dir = os.path.abspath(project_dir)
        self._project_dir = project_dir
        config_file = os.path.join(project_dir, options.config_file)
        config = VirtstrapConfig.from_file(config_file, 
                profiles=options.profiles)
        processor = ProjectNameProcessor(project_dir)
        project_name = config.process_section('project_name', processor)
        self._project_name = project_name
        self._config = config
        self._config_file = config_file
        self._options = options

    def _find_project_dir(self):
        return find_project_dir()

    @property
    def name(self):
        return self._project_name

    @property
    def config_file(self):
        if not os.path.isfile(self._config_file):
            return None
        return self._config_file

    def set_options(self, options):
        self._options = options

    def path(self, *paths):
        """Create a path relative to the project"""
        return os.path.join(self._project_dir, *paths)

    def env_path(self, *paths):
        """Create a path relative to the virtstrap-dir"""
        return os.path.join(self._project_dir, 
                self._options.virtstrap_dir, *paths)

    def bin_path(self, *paths):
        """Create a path relative to the virtstrap-dir's bin directory"""
        return self.env_path('bin', *paths)

    def process_config_section(self, section, processor):
        return self._config.process_section(section, processor)

    def config(self, section):
        """Grabs processed section data"""
        return self._config.processed(section)

    def call_bin(self, command_name, args, **options):
        command = [self.bin_path(command_name)]
        command.extend(args)
        return call_subprocess(command, **options)

class NoProjectFound(Exception):
    pass

def find_project_dir(current_dir=None):
    """Finds the project directory for the current directory"""
    current_dir = current_dir or os.path.abspath(os.curdir)
    if VIRTSTRAP_DIR in os.listdir(current_dir):
        vs_dir = os.path.join(current_dir, VIRTSTRAP_DIR)
        if os.path.islink(vs_dir) or os.path.isdir(vs_dir):
            return current_dir
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    if parent_dir == current_dir:
        raise NoProjectFound('No project found')
    return find_project_dir(parent_dir)

class ProjectNameProcessor(object):
    def __init__(self, project_dir):
        self._project_dir = os.path.abspath(project_dir)

    def __call__(self, project_name):
        return project_name or os.path.basename(self._project_dir)
