"""
virtstrap.commands.clean
------------------------

The 'clean' command
"""
import os
import shutil
from virtstrap import commands
from virtstrap import constants

class CleanCommand(commands.ProjectCommand):
    """Cleans up any files that belong to virtstrap.
    
    This excludes VEfile and requirements.lock
    """
    name = 'clean'
    description = 'Remove virtstrap environment from your project'

    def run(self, project, options, **kwargs):
        self.remove_virtstrap_environment(project)
        self.remove_quick_activate_script(project)

    def remove_virtstrap_environment(self, project):
        """Remove the virtstrap environment"""
        env_path = project.env_path()
        if os.path.islink(env_path):
            env_path = os.path.realpath(env_path)
        shutil.rmtree(env_path)
        # Check if .vs.env is a symlink and delete if it is
        relative_virtstrap_dir = project.path(constants.VIRTSTRAP_DIR)
        if os.path.islink(relative_virtstrap_dir):
            os.remove(relative_virtstrap_dir)

    def remove_quick_activate_script(self, project):
        quick_activate_path = project.path(constants.QUICK_ACTIVATE_FILENAME)
        if os.path.exists(quick_activate_path) and \
                os.path.isfile(quick_activate_path):
            os.remove(quick_activate_path)
