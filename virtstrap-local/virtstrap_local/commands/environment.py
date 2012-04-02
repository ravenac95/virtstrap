"""
virtstrap.commands.install
--------------------------

The 'install' command
"""
import os
import tempfile
import subprocess
from contextlib import contextmanager
from virtstrap.argparse import ArgumentParser
from virtstrap import commands
from virtstrap import constants
from virtstrap.requirements import RequirementSet
from virtstrap.locker import *

parser = ArgumentParser()
parser.add_argument('env_file', metavar='FILE',
        help="file to write extra environment")

class EnvironmentCommand(commands.ProjectCommand):
    name = 'environment'
    description = "Writes extra environment variables to a file"
    parser = parser

    def run(self, project, options, **kwargs):
        environment_vars = self.get_environment_vars(project)
        self.write_environment_vars_to_file(options, environment_vars)

    def process_environment_config(self, raw_environment):
        project = self.project
        raw_environment = raw_environment or {}
        replacement_vars = {
            '$VE_DIR': project.env_path(),
            '$BIN_DIR': project.bin_path(),
            '$PROJECT_DIR': project.path(),
        }
        def replace_vars(string):
            replaced = string
            for search, replacement in replacement_vars.iteritems():
                replaced = replaced.replace(search, replacement)
            return replaced
        environment = {}
        for variable, raw_value in raw_environment.iteritems():
            value = replace_vars(raw_value)
            environment[variable] = value
        return environment
    
    def get_environment_vars(self, project):
        environment_vars = project.process_config_section('environment',
                                self.process_environment_config)
        return environment_vars

    def write_environment_vars_to_file(self, options, environment_vars):
        env_file = options.env_file
        output = open(env_file, 'w')
        variable_names = []
        for variable, value in environment_vars.iteritems():
            self.write_environment_var(output, variable, value)
            variable_names.append(variable)
        output.close()

    def write_environment_var(self, output, variable, value):
        # Use a temp_var so we don't have to escape
        value = value.replace(" ", "\ ")
        output.write('add_custom_virtstrap_var %s "%s"\n' % (variable, value))
        #output.write('export %s\n' % variable)
