"""
virtstrap.testing.fakes
-------------------------

Test tools to create fake objects related to virtstrap
"""
from contextlib import contextmanager
import virtualenv
import fudge
from virtstrap.testing import *
from virtstrap import constants
from virtstrap import commands
from virtstrap import hooks
from virtstrap.project import Project
from virtstrap.options import create_base_parser

FakeProject = shunt_class(Project)

def fake_command(name):
    class FakeCommand(commands.Command, ShuntMixin):
        name = None
        def run(self):
            return 0
    FakeCommand.name = name
    return FakeCommand

def fake_hook(name, command='command', events=None):
    events = events or ['event']
    class FakeGeneratedHook(hooks.GeneratedHook, ShuntMixin):
        pass
    def fake_hook_function(*args, **kwargs):
        pass
    return FakeGeneratedHook(name, command, events, fake_hook_function)

@contextmanager
def temp_project(change_working_dir=True):
    """Creates a temporary project directory within a temporary directory
    
    This is useful for testing ProjectCommands.
    """
    base_parser = create_base_parser()
    options = base_parser.parse_args(args=[])
    dir_context = in_temp_directory
    if not change_working_dir: 
        dir_context = temp_directory
    with dir_context() as temp_dir:
        vs_dir_path = os.path.join(temp_dir, constants.VIRTSTRAP_DIR)
        os.mkdir(vs_dir_path)
        virtualenv.create_environment(vs_dir_path,
                site_packages=False)
        options.project_dir = temp_dir
        project = FakeProject.load(options)
        yield project, options, temp_dir
