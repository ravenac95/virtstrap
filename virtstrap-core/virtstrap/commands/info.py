"""
virtstrap.commands.info
-----------------------

The 'info' command
"""

import os
import shutil
from virtstrap import commands
from virtstrap import constants

class InfoCommand(commands.ProjectCommand):
    """Displays information about the current project
    
    This excludes VEfile and requirements.lock
    """
    name = 'info'
    description = 'Displays information about current project'

    def run(self, project, options, **kwargs):
        self.display_info(project)

    def display_info(self, project):
        self.logger.info('*******************%s INFO*******************\n' % project.name)
        self.logger.info('Project Path: %s' % project.path())
        self.logger.info('Project Environment Path: %s' % project.env_path())
        self.logger.info('Project Bin Path: %s' % project.bin_path())
