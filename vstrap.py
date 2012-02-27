#!/usr/bin/env python
#coding=utf-8
"""
VirtualEnvironment Bootstrap
============================

zc.buildout is a great system for many different purposes. However,
for quick prototyping of libraries and flexibility of using easy_install
or pip virtualenv has the edge on buildout. The one major function that 
virtualenv does not have is easy repeatability. This script attempts
to remedy that by creating a special bootstrap for virtualenv that has the
ability to use buildout, pip, a list of unix commands, or any combination of
those three options to introduce repeatability to your programs.
"""
from optparse import OptionParser
from subprocess import call
import json
import os, sys
import platform
import urllib

VIRTUALENV_INSTALLED = True
try:
    import virtualenv
except ImportError:
    VIRTUALENV_INSTALLED = False

if platform.system() == "Windows":
    print "virtstrap is only made for posix systems. Sorry."
    sys.exit(1)

##########################################
# Program Constants                      #
##########################################
EXIT_WITH_ERROR = 1
EXIT_NORMALLY = 0
VIRTUALENV_PROMPT_TEMPLATE = "({0}env) "
DEFAULT_SETTINGS_FILENAME = "vsettings.json"

DEFAULT_SETTINGS = dict(
    package_name="",
    use_site_packages=False,
    virtualenv_dir="./vs.env/",
    env_types=[], #Possible values command_list, pip, buildout
    # buildout bootstrap url so it can be downloaded. 
    # It's long so it was split into two lines (if that wasn't obvious)
    buildout_bin_path="bin/",
    buildout_bootstrap_url=("http://svn.zope.org/*checkout*/" 
        "zc.buildout/trunk/bootstrap/bootstrap.py"),
)

##########################################
# Command line input functions           #
##########################################
def yes_no_input(prompt, default=True):
    default_input_string = "[Y/n]"
    if not default:
        default_input_string = "[y/N]"
    while True:
        raw_result = raw_input_with_default(prompt, default_input_string)
        if not raw_result.lower() in ["yes", "no", "y", "n"]:
            print "Please only input yes, no, y, or n"
        else:
            if raw_result.startswith('y'):
                result = True
            else:
                result = False
    return result

def raw_input_with_default(prompt, default_input_string="['']"):
    return raw_input("{0} {1}:".format(prompt, default_input_string))

##########################################
# Exit functions                         #
##########################################

def exit_with_error():
    print "Exiting. virtstrap task incomplete."
    sys.exit(EXIT_WITH_ERROR)

def exit_normally():
    print "virtstrap task completed."
    sys.exit(EXIT_NORMALLY)

##########################################
# Utility functions                      #
##########################################
def in_virtualenv():
    if hasattr(sys, 'real_prefix'):
        return True
    return False

def find_file_or_skip(file, not_found_string="'{0}' not found."):
    file_found = True
    if not os.path.isfile(file):
        file_found = False
        print not_found_string.format(file)
        if options.interactive:
            exit_with_error()
        else:
            if yes_no_input("Skip?"):
                print "Skipping."
            else:
                exit_with_error()
    return file_found

def find_all_files_or_skip(files, not_found_string="Files not found."):
    files_found = True
    if not all_files_exist(files):
        files_found = False
        print not_found_string
        if not options.interactive:
            exit_with_error()
        else:
            if yes_no_input("Skip?"):
                print "Skipping."
            else:
                exit_with_error()
    return files_found

def all_files_exist(files):
    for file in files:
        if not os.path.isfile(file):
            return False
    return True

def get_virtualenv_dir_abspath():
    return os.path.abspath(settings['virtualenv_dir'])

def make_current_settings(settings_filename, default_settings=None):
    """Compile settings from default and user"""
    # Set default settings
    if not default_settings:
        default_settings = DEFAULT_SETTINGS
    # Try opening the settings file
    try:
        settings_file = open(settings_filename)
    except IOError:
        #If file isn't found tell the user and exit with error
        print ("A settings file is required. Could not find {0}"
                .format(settings_filename))
        exit_with_error()
    # Load json from file. (The file, currently, must be json)
    user_defined_settings = json.load(settings_file)

    # Build settings keys
    settings_keys = user_defined_settings.keys()

    # Copy defaults into a new settings dictionary
    current_settings = default_settings.copy()

    # Check that a package name is defined
    package_name = user_defined_settings.get('package_name')
    if not package_name:
        #If there isn't a package name then tell user and exit with error
        print "At least a package name is required for virtstrap.py"
        exit_with_error()
    
    # There are some built in defaults

    # Create the default virtualenv prompt using the package name
    prompt = VIRTUALENV_PROMPT_TEMPLATE.format(package_name)
    current_settings['prompt'] = prompt

    # Add the user defined settings to the new settings dictionary
    for key in settings_keys:
        current_settings[key] = user_defined_settings[key]
    return current_settings

##########################################
# Environment type commands              #
##########################################

def pip_requirements_builder(**kwargs):
    """Builds pip requirements"""
    virtualenv_dir_abspath = get_virtualenv_dir_abspath()
    try:
        pip_requirements_file = settings['pip_requirements_file']
    except KeyError:
        print "Pip env_type requires setting 'pip_requirements_file'"
        exit_with_error()
    
    if find_file_or_skip(pip_requirements_file):
        pip_bin = "{0}/bin/pip".format(
                virtualenv_dir_abspath)
        pip_command = "install"
        call([pip_bin, "install", "-r", pip_requirements_file])

def shell_script_executor(**kwargs):
    try:
        shell_script_file = settings['shell_script_file']
    except KeyError:
        print "Shell Script env_type requires a setting 'command_list_file'"
        exit_with_error()
    if find_file_or_skip(shell_script_file):
        call(["sh", shell_script_file])

def buildout_builder(**kwargs):
    bootstrap_py = "bootstrap.py"

    buildout_cfg = settings.get('buildout_config_file', 'buildout.cfg')
    buildout_cfg_found = find_file_or_skip(buildout_cfg, 
            not_found_string=("Buildout needs the specified buildout config "
                "file ({0}) present"))
    
    # Download bootstrap.py
    if not os.path.isfile(bootstrap_py):
        urllib.urlretrieve(settings['buildout_bootstrap_url'], bootstrap_py)
    if not os.path.isfile(bootstrap_py):
        print "Error Downloading {0}".format(bootstrap_py)
        exit_with_error()
    
    # Get virtualenv interpreter to use for bootstrapping
    virtualenv_dir_abspath = get_virtualenv_dir_abspath()
    virtualenv_python_bin = os.path.join(virtualenv_dir_abspath, "bin/python")
    # Get path to buildout executable or go to default buildout setting
    buildout_bin_path = settings.get('buildout_bin_path')
    buildout_executable = os.path.join(buildout_bin_path, "buildout")
    if buildout_cfg_found:
        if not os.path.isfile(buildout_executable):
            call([virtualenv_python_bin, bootstrap_py])
        if not os.path.isfile(buildout_executable):
            print "Cannot find buildout executable"
            exit_with_error()
        call([buildout_executable,  "-c", buildout_cfg])

##########################################
# Script Commands                        #
##########################################

def bootstrap():
    """The default command for this script"""
    create_virtualenv()
    run_build()

def create_virtualenv():
    """Create the virtual environment"""
    if not VIRTUALENV_INSTALLED:
        message = ("In order to bootstrap with virtstrap. "
                "You need virtualenv installed and you "
                "should not be in an active virtualenv")
        print message
        exit_with_error()
    if in_virtualenv():
        message = ("WARNING: You are currently in an active virtualenv. "
                "This is highly discouraged.")
        print message
        exit_with_error()
    # Create a virtual environment directory
    virtualenv_dir = settings['virtualenv_dir']
    virtualenv_dir_abspath = get_virtualenv_dir_abspath()
    print "Creating Virtual Environment in {0}".format(virtualenv_dir_abspath)
    virtualenv.create_environment(settings['virtualenv_dir'], 
            site_packages=settings['use_site_packages'], 
            prompt=settings['prompt'])
    # Create activation script
    print "Create quickactivate.sh script for virtualenv"
    quick_activation_script(virtualenv_dir_abspath)


def quick_activation_script(virtualenv_dir, file="quickactivate.sh", 
        base_path='./'):
    """Builds a virtualenv activation script shortcut"""
    quick_activate_filename = os.path.join(base_path, file)
    quick_activate_file = open(quick_activate_filename, 'w')
    quick_activate_file.writelines(["#!/bin/bash\n", 
        "source {0}/bin/activate".format(virtualenv_dir)])
    quick_activate_file.close()

def run_build():
    """Build the project based on the env_types"""
    env_types = settings['env_types']
    for env_type in env_types:
        builder = ENVIRONMENT_TYPE_BUILDERS.get(env_type)
        if not builder:
            print "env_type: {0}. Does not exist".format(env_type)
            if not options.interactive:
                exit_with_error()
            else:
                if yes_no_input("Skip?"):
                    print "Skipping."
                else:
                    exit_with_error()
        builder()

##########################################
# Program settings                       #
##########################################

VIRTSTRAP_COMMANDS = dict(
    default=bootstrap,
    build=run_build
)

ENVIRONMENT_TYPE_BUILDERS = dict(
    pip=pip_requirements_builder,
    shell_script=shell_script_executor,
    buildout=buildout_builder,
)

parser = OptionParser()
parser.add_option("-n", "--no-build", dest="no_build",
        help="Only setup virtual environment")
parser.add_option("-s", "--install-settings", dest="install_settings",
        help=("The settings JSON file defaults to {0}"
            .format(DEFAULT_SETTINGS_FILENAME)), 
        default=DEFAULT_SETTINGS_FILENAME)
parser.add_option("-i", "--interactive", dest="interactive",
        help="Turns on interactivity", 
        default=False)

options, args = parser.parse_args() #Global options and args

settings = None # Global settings for the script

##########################################
# Main                                   #
##########################################
def main():
    # If there aren't args set command to default
    if len(args) == 0:
        command_name = "default"
    else:
        # Otherwise use the first argument as the command
        command_name = args[0]
    # Compile settings into global settings variable
    global settings
    settings = make_current_settings(options.install_settings)

    # Choose virtstrap command from dictionary of commands
    virtstrap_command = VIRTSTRAP_COMMANDS.get(command_name)
    # If the virtstrap command doesn't exist then exit with error
    if not virtstrap_command:
        print "'{0}' is not a valid command".format(command_name)
        exit_with_error()
    virtstrap_command()
    exit_normally()

if __name__ == "__main__":
    main()
