"""
Runner Tests
============

Very high level tests for the virtstrap runner. 
"""
import os
import sys
import fudge
from cStringIO import StringIO
from tests import fixture_path
from virtstrap.testing import *
from nose.tools import raises
from nose.plugins.attrib import attr
from virtstrap import constants
from virtstrap.runner import VirtstrapRunner

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../'))
PACKAGES_DIR = os.path.abspath(os.path.join(PROJECT_DIR,
                    'tests/fixture/packages'))

TEST_CONFIG = """
requirements:
  - test1
  - test5

--- # Development profile
profile: development

requirements:
  - test4

---
profile: production

requirements:
  - test6
"""

def test_initialize_runner():
    """Test that we can initialize the VirtstrapRunner"""
    runner = VirtstrapRunner()

@fudge.test
def test_runner_lazy_load_registry():
    """Use a registry factory method to lazily load a registry"""
    fake_registry_factory = fudge.Fake()
    fake_registry_factory.expects_call().returns('reg')
    runner = VirtstrapRunner(registry_factory=fake_registry_factory)
    registry = runner.registry
    runner.set_registry('regtest')
    assert runner.registry == 'regtest'

@fudge.test
def test_runner_lazy_load_loader():
    """Use a loader factory method to lazily load a loader"""
    fake_loader_factory = fudge.Fake()
    fake_loader_factory.expects_call().returns('regtest')
    runner = VirtstrapRunner(loader_factory=fake_loader_factory)
    loader = runner.loader
    runner.set_loader('regtest')
    # Test the injected loader
    assert runner.loader == 'regtest'

class TestVirtstrapRunner(object):
    def setup(self):
        self.runner = VirtstrapRunner()

    def teardown(self):
        self.runner = None
    
    @fudge.test
    def test_runner_lists_commands(self):
        fake_registry = fudge.Fake()
        (fake_registry.expects('list_commands')
                .returns(['command1', 'command2']))
        self.runner.set_registry(fake_registry)
        commands = self.runner.list_commands()
        assert commands == ['command1', 'command2']

    @fudge.test
    def test_runner_run_command(self):
        """Test that the runner passes the correct data to the registry"""
        args = ('test', 'options')
        fake_registry = fudge.Fake()
        fake_registry.expects('run').with_args(*args)
        self.runner.set_registry(fake_registry)
        self.runner.run_command(*args)

    @fudge.patch('sys.stderr')
    def test_run_no_args(self, fake_stderr):
        """Run the main command line utility with no args"""
        fake_stderr.is_a_stub() # just want to silence stderr
        try:
            return_code = self.runner.main()
        except SystemExit, e:
            system_exit = True
            assert e.code == 2
        assert system_exit == True, "Runner didn't issue a system exit"

    def test_run_help(self):
        """Run help"""
        test_args = ['--help']
        system_exit = False
        try:
            code = self.runner.main(args=test_args)
        except SystemExit, e:
            system_exit = True
            assert e.code == 0
        assert system_exit == True, "Runner didn't issue a system exit"
