"""
Runner Tests
============

Very high level tests for the virtstrap runner. 
"""
import os
import sys
import fudge
from virtstrap import constants
from virtstrap.runner import VirtstrapRunner
from virtstrap_system.runner import VirtstrapSystemWideRunner

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../'))

def test_initialize_runner():
    """Test that we can initialize the VirtstrapRunner"""
    runner = VirtstrapSystemWideRunner()
    assert isinstance(runner, VirtstrapRunner)

class TestVirtstrapSystemWideRunner(object):
    def setup(self):
        self.runner = VirtstrapSystemWideRunner()
    
    def test_loads_commands(self):
        runner = self.runner
        commands = runner.load_commands()
        commands = runner.list_commands()
        commands_set = set(commands)
        assert commands_set == set(['init', 'commands'])
    
    @fudge.patch('virtstrap.project.call_subprocess')
    def test_loads_commands_with_project_commands(self, fake_call_sub):
        runner = self.runner
        (fake_call_sub.expects_call()
                .with_args(['/pdir/.vs.env/bin/virtstrap-local', 'commands', '--as-json'], 
                    collect_stdout=True)
                .returns('{"commands": [{"name": "install", "description": "desc"}]}'))
        runner.set_args(['--project-dir=/pdir'])
        commands = runner.load_commands()
        commands = runner.list_commands()
        commands_set = set(commands)
        assert commands_set == set(['init', 'commands', 'install'])


    @fudge.patch('virtstrap.project.call_subprocess')
    def test_runs_project_command(self, fake_call_sub):
        runner = self.runner
        (fake_call_sub.expects_call()
                .with_args(['/pdir/.vs.env/bin/virtstrap-local', 'commands', '--as-json'], 
                    collect_stdout=True)
                .returns('{"commands": [{"name": "install", "description": "desc"}]}')
                .next_call()
                .with_args(['/pdir/.vs.env/bin/virtstrap-local', 'install', '--project-dir=/pdir']))
        return_code = runner.main(args=['install', '--project-dir=/pdir'])
    
    @fudge.patch('virtstrap.project.call_subprocess')
    def test_runs_project_command_with_extra_options(self, fake_call_sub):
        runner = self.runner
        (fake_call_sub.expects_call()
                .with_args(['/pdir/.vs.env/bin/virtstrap-local', 'commands', '--as-json'], 
                    collect_stdout=True)
                .returns('{"commands": [{"name": "install", "description": "desc"}]}')
                .next_call()
                .with_args(['/pdir/.vs.env/bin/virtstrap-local', 'install', 
                    '--project-dir=/pdir', '--opt1', '--opt2=opt2']))
        return_code = runner.main(args=['install', '--project-dir=/pdir', 
                            '--opt1', '--opt2=opt2'])
