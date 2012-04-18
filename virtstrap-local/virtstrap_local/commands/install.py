"""
virtstrap.commands.install
--------------------------

The 'install' command
"""
import os
import tempfile
import subprocess
from contextlib import contextmanager
from virtstrap import commands
from virtstrap import constants
from virtstrap.requirements import RequirementSet
from virtstrap.locker import *

def process_requirements_config(raw_requirements):
    requirement_set = RequirementSet.from_config_data(raw_requirements)
    return requirement_set

class InstallationError(Exception):
    pass

class InstallCommand(commands.ProjectCommand):
    name = 'install'
    description = "Installs the project's python requirements"

    def run(self, project, options, **kwargs):
        requirement_set = self.get_requirement_set(project)
        if requirement_set:
            # Check for lock file if it exists then use it.
            locked_reqs_string = self.get_lock_file_requirement_set(project)
            temp_reqs_path = self.write_temp_requirements_file(
                    requirement_set, locked_reqs_string)
            try:
                self.run_pip_install(project, temp_reqs_path)
            except:
                raise
            else:
                self.freeze_requirements(project, requirement_set)
            finally:
                os.remove(temp_reqs_path)

    def get_requirement_set(self, project):
        requirement_set = project.process_config_section('requirements',
                                process_requirements_config)
        return requirement_set

    def write_temp_requirements_file(self, requirement_set, locked_reqs_string):
        requirements_joiner = RequirementsJoiner()
        requirements_write = requirements_joiner.join_to_str(
                requirement_set=requirement_set,
                locked_string=locked_reqs_string)
        os_handle, temp_reqs_path = tempfile.mkstemp()
        temp_reqs_file = open(temp_reqs_path, 'w')
        temp_reqs_file.write(requirements_write)
        temp_reqs_file.close()
        return temp_reqs_path

    def get_lock_file_requirement_set(self, project):
        lock_file_path = project.path(constants.VE_LOCK_FILENAME)
        try:
            locked_requirements = open(lock_file_path, 'r')
        except IOError:
            return ''
        return locked_requirements.read()
        
    def run_pip_install(self, project, requirements_path):
        logger = self.logger
        logger.info('Building requirements in "%s"' % project.config_file)
        pip_bin = project.bin_path('pip')
        pip_command = 'install'
        self.logger.debug('Running pip at %s' % pip_bin)
        return_code = subprocess.call([pip_bin, pip_command, '-r', 
            requirements_path])
        if return_code != 0:
            raise InstallationError('An error occured during installation')

    def freeze_requirements(self, project, requirement_set):
        locker = RequirementsLocker()
        lock_str = locker.lock(requirement_set)
        requirements_lock = open(project.path(constants.VE_LOCK_FILENAME), 'w')
        requirements_lock.write(lock_str)
        requirements_lock.close()

    def freeze_requirements_old(self, project, requirement_set):
        pip_bin = project.bin_path('pip')
        process = subprocess.Popen([pip_bin, 'freeze'],
                stdout=subprocess.PIPE)
        requirements = process.stdout.read()
        requirements_lock = open(project.path(constants.VE_LOCK_FILENAME), 'w')
        requirements_lock.write(requirements)
        requirements_lock.close()
