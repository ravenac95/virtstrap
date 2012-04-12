"""
virtstrap.commands.init
-----------------------

The 'init' command
"""
import os
import sys
import shutil
import tempfile
from virtstrap.argparse import ArgumentParser
from virtstrap import commands
from virtstrap import constants
from virtstrap.options import base_options_to_args
from virtstrap.requirements import RequirementSet
from virtstrap_system.loaders import call_project_command

parser = ArgumentParser()
parser.add_argument('project_dir', metavar='PROJECT_DIR',
        help="project's root directory",
        nargs='?', default='.')

def process_plugins_config(raw_plugins):
    requirement_set = RequirementSet.from_config_data(raw_plugins)
    return requirement_set

class InitializeCommand(commands.ProjectCommand):
    name = 'init'
    parser = parser
    description = 'Bootstraps a virtstrap virtual environment'

    def run(self, project, options, raw_args=None, use_injected_project=False, 
            **kwargs):
        # FIXME the init command automatically reloads the project settings
        # because it is the only command that can take the project directory name
        # as a positional argument
        if not use_injected_project:
            project = self.load_project(options)
        self.project = project
        self.ensure_project_directory(project)
        self.create_virtualenv(project, options)
        self.wrap_activate_script(project)
        self.create_quick_activate_script(project)
        self.run_install_for_project(project, options)

    def ensure_project_directory(self, project):
        project_dir = project.path()
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

    def create_virtualenv(self, project, options):
        """Create virtual environment in the virtstrap directory"""
        import virtualenv
        virtstrap_dir = project.env_path()
        project_name = project.name
        self.logger.info('Creating virtualenv in %s for "%s"' % (
            virtstrap_dir, project_name))
        # Create the virtualenv
        virtualenv.create_environment(virtstrap_dir,
                site_packages=False,
                prompt="(%s) " % project_name)
        expected_virtstrap_dir = project.path(constants.VIRTSTRAP_DIR)
        if virtstrap_dir != expected_virtstrap_dir:
            # if the expected project path isn't there then make sure
            # we have a link at the expected location.
            os.symlink(virtstrap_dir, expected_virtstrap_dir)

        # Install virtstrap into virtualenv
        # FIXME add later. with optimizations. This is really slow
        self.install_virtstrap(project)
        self.install_virtstrap_plugins(project)
        self.setup_config_folder(project, options)

    def install_virtstrap(self, project):
        try:
            import virtstrap_support
        except ImportError:
            self.logger.error('Virtstrap is improperly installed or '
                    'being called from inside another virtstrap. Please '
                    'check your installation.')
            sys.exit(2)
        # Set the directory to the correct files
        pip_bin = 'pip'
        pip_command = 'install'
        pip_find_links = ('--find-links=file://%s' % 
                virtstrap_support.file_directory())
        pip_args = [pip_command, pip_find_links, '--no-index', '--quiet',
                'virtstrap-local']
        # TODO REMOVE dev once we're ready
        # Add a test for this 
        self.logger.debug('Installing virtstrap into environment')
        try:
            project.call_bin(pip_bin, pip_args, show_stdout=False)
        except OSError:
            self.logger.error('An error occured with pip')
            sys.exit(2)

    def setup_config_folder(self, project, options):
        # Create the folder
        config_path = project.env_path('config')
        if not os.path.isdir(config_path):
            os.makedirs(config_path)

        # Create the profiles config
        profiles_file_path = os.path.join(config_path, 'profiles')
        profiles_file = open(profiles_file_path, 'w')
        
        profiles_string = ",".join(options.profiles)
        profiles_file.write(profiles_string)
        profiles_file.close()

    def install_virtstrap_plugins(self, project):
        self.logger.info('Installing any virtstrap plugins')
        plugin_set = project.process_config_section('plugins', 
                process_plugins_config)
        temp_reqs_path = self.write_temp_requirements_file(plugin_set)
        project.call_bin('pip', ['install', '-r', temp_reqs_path], 
                show_stdout=False)
        os.remove(temp_reqs_path)
        
    def write_temp_requirements_file(self, requirement_set):
        requirements_write = requirement_set.to_pip_str()
        os_handle, temp_reqs_path = tempfile.mkstemp()
        temp_reqs_file = open(temp_reqs_path, 'w')
        temp_reqs_file.write(requirements_write)
        temp_reqs_file.close()
        return temp_reqs_path
        
    def wrap_activate_script(self, project):
        """Creates a wrapper around the original activate script"""
        self.logger.info('Wrapping original activate script')
        # Copy old activate script
        activate_path = project.bin_path('activate') # The normal path
        old_activate_path = project.bin_path('ve_activate') # Dest path
        shutil.copy(activate_path, old_activate_path)

        # Using a template, create the new one
        new_activate_script = self.render_template('init/activate.sh.tmpl')
        activate_file = open(activate_path, 'w')
        activate_file.write(new_activate_script)

    def create_quick_activate_script(self, project):
        """Create a quickactivate script

        This script is purely for convenience. Eventually it will be made
        optional and something more convenient will be provided. However,
        at this time. This makes it much easier than typing in

            $ source .vs.env/bin/activate
        """
        self.logger.info('Creating quick activate script')
        quick_activate_path = project.path(constants.QUICK_ACTIVATE_FILENAME)
        quick_activate_script = self.render_template(
                'init/quickactivate.sh.tmpl')
        quick_activate = open(quick_activate_path, 'w')
        quick_activate.write(quick_activate_script)
        quick_activate.close()

    def run_install_for_project(self, project, options):
        self.logger.debug('Running install command for project')
        args = base_options_to_args(options)
        call_project_command(project, 'install', args)
