"""
virtstrap.commands.install
--------------------------

The 'install' command
"""
import os
import tempfile
import subprocess
from virtstrap import commands
from virtstrap import constants
from virtstrap.argparse import ArgumentParser
from virtstrap.requirements import RequirementSet
from virtstrap.locker import *
from virtstrap.joined import *


def process_requirements_config(raw_requirements):
    requirement_set = RequirementSet.from_config_data(raw_requirements)
    return requirement_set


class InstallationError(Exception):
    pass


parser = ArgumentParser()
parser.add_argument('--upgrade', '-U', action="store_true",
        help='Upgrade the requirements and update lock file')


class InstallCommand(commands.ProjectCommand):
    name = 'install'
    description = "Installs the project's python requirements"
    parser = parser

    def run(self, project, options, **kwargs):
        requirement_set = self.get_requirement_set(project)
        upgrade = options.upgrade
        if requirement_set:
            # Check for lock file if it exists then use it.
            locked_reqs = self.get_locked_requirement_set(project,
                    upgrade)
            temp_reqs_path = self.write_temp_requirements_file(
                    requirement_set, locked_reqs)
            try:
                self.run_pip_install(project, temp_reqs_path, upgrade)
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

    def write_temp_requirements_file(self, requirement_set, locked_reqs):
        joined = JoinedRequirementSet.join(requirement_set, locked_reqs)
        os_handle, temp_reqs_path = tempfile.mkstemp()
        temp_reqs_file = open(temp_reqs_path, 'w')
        for requirement in joined.as_list():
            temp_reqs_file.write('%s\n' % requirement.to_pip_str())
        temp_reqs_file.close()
        return temp_reqs_path

    def get_locked_requirement_set(self, project, upgrade):
        lock_file_path = project.path(constants.VE_LOCK_FILENAME)
        locked_requirements = LockedRequirementSet.from_string('')
        # If we're doing an upgrade then ignore the locked requirements
        if upgrade:
            return locked_requirements
        try:
            locked_requirements = LockedRequirementSet.from_file(
                    lock_file_path)
        except IOError:
            return locked_requirements
        return locked_requirements

    def run_pip_install(self, project, requirements_path, upgrade):
        logger = self.logger
        logger.info('Building requirements in "%s"' % project.config_file)
        pip_bin = project.bin_path('pip')
        pip_command = 'install'
        self.logger.debug('Running pip at %s' % pip_bin)

        command_args = [pip_bin, pip_command, '-r', requirements_path]

        if upgrade:
            command_args.append('--upgrade')

        return_code = subprocess.call(command_args)
        if return_code != 0:
            raise InstallationError('An error occured during installation')

    def freeze_requirements(self, project, requirement_set):
        locker = RequirementsLocker()
        lock_str = locker.lock(requirement_set)
        requirements_lock = open(project.path(constants.VE_LOCK_FILENAME), 'w')
        requirements_lock.write(lock_str)
        requirements_lock.close()
