import sys
import os
import fudge
from fudge.patcher import patch_object
from nose.plugins.attrib import attr
from tests import fixture_path
from virtstrap import constants
from virtstrap.testing import *
from virtstrap_local.commands.environment import EnvironmentCommand

def test_environment_config_processing():
    with temp_project() as context:
        project, options, temp_dir = context
        project.__patch_method__('env_path').returns('env')
        project.__patch_method__('bin_path').returns('bin')
        project.__patch_method__('path').returns('proj')
        command = EnvironmentCommand()
        command.project = project
        environment = command.process_environment_config(dict(
            a="$VE_DIR",
            b="$BIN_DIR",
            c="$PROJECT_DIR",
            d="HELLO",
            e="$PROJECT_DIR/hello",
        ))
        expected = [
            ('a', 'env'),
            ('b', 'bin'),
            ('c', 'proj'),
            ('d', 'HELLO'),
            ('e', 'proj/hello'),
        ]
        for var, value in expected:
            assert environment[var] == value

@attr('slow')
def test_environment_runs_without_settings():
    with temp_project() as context:
        project, options, temp_dir = context
        vefile = open('VEfile', 'w')
        vefile.write("")
        vefile.close()
        from virtstrap_local.runner import main
        temp_env_file_path = os.path.join(temp_dir, 'temp_env_file')
        main(args=['environment', temp_env_file_path])
