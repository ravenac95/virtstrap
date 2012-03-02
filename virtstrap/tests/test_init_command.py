"""
Initialize Command
==================

Very high level tests for the virtstrap runner
"""
import os
import sys
import fudge
import subprocess
from nose.tools import raises
from nose.plugins.attrib import attr
from virtstrap import constants
from virtstrap.testing import *
from virtstrap.options import create_base_parser
from virtstrap_system.commands.init import InitializeCommand

def test_initialize_command():
    command = InitializeCommand()

@attr('slow')
@fudge.patch('virtstrap_system.commands.init.call_project_command')
def test_run_initialize_command(fake_call):
    fake_call.expects_call()
    with in_temp_directory() as temp_directory:
        command = InitializeCommand()
        parser = create_base_parser()
        options = parser.parse_args(['--project-dir=.'])
        return_code = command.execute(options)
        pip_bin = os.path.join(temp_directory, constants.VIRTSTRAP_DIR, 
                'bin', 'pip')
        output, ret = call_and_capture([pip_bin, 'freeze'])
        expected_packages = ['simpleyaml', 'virtstrap-core', 
                'virtstrap-local', 'Jinja2']
        for expected in expected_packages:
            assert expected in output
        assert return_code == 0

@attr('slow')
@fudge.patch('virtstrap_system.commands.init.call_project_command')
def test_run_initialize_command_in_subdirectory(fake_call):
    fake_call.expects_call()
    """Init command using a subdirectory of CWD for the project"""
    with in_temp_directory() as temp_directory:
        project_dir = os.path.join(temp_directory, 'projdir')
        command = InitializeCommand()
        parser = create_base_parser()
        options = parser.parse_args(['--project-dir=%s' % project_dir])
        return_code = command.execute(options)
        pip_bin = os.path.join(project_dir, constants.VIRTSTRAP_DIR, 
                'bin', 'pip')
        output, ret = call_and_capture([pip_bin, 'freeze'])
        expected_packages = ['simpleyaml', 'virtstrap-core', 
                'virtstrap-local', 'Jinja2']
        for expected in expected_packages:
            assert expected in output
        assert return_code == 0

@attr('slow')
@fudge.patch('virtstrap_system.commands.init.call_project_command')
def test_run_initialize_command_in_many_subdirectories(fake_call):
    """Init command using a subdirectory of CWD for the project and virtstrap
    """
    fake_call.expects_call()
    with in_temp_directory() as temp_directory:
        project_dir = os.path.join(temp_directory, 'projdir')
        virtstrap_dir = os.path.join(temp_directory, 'vsdir')
        command = InitializeCommand()
        parser = create_base_parser()
        options = parser.parse_args(['--project-dir=%s' % project_dir, 
            '--virtstrap-dir=%s' % virtstrap_dir])
        return_code = command.execute(options)
        pip_bin = os.path.join(project_dir, constants.VIRTSTRAP_DIR, 
                'bin', 'pip')
        output, ret = call_and_capture([pip_bin, 'freeze'])
        expected_packages = ['simpleyaml', 'virtstrap-core',
                'virtstrap-local', 'Jinja2']
        for expected in expected_packages:
            assert expected in output
        assert return_code == 0
