"""
Test Base Command
-----------------
"""
import fudge
from nose.tools import *
from tests import fixture_path
from virtstrap.testing import *
from virtstrap.templating import temp_template_environment
from virtstrap.basecommand import Command, ProjectMixin, ProjectCommand

class FakeCommand(Command):
    name = 'fake'
    args = ['argument_one']
    description = 'Fake Description'

    def __init__(self, test_obj):
        super(FakeCommand, self).__init__()
        self.test_obj = test_obj

    def run(self, *args, **kwargs):
        self.test_obj.write("This is a test")


def assert_called_flag(command, message=None):
    """A useful shortcut for testing sub classes"""
    message = message or 'Command.called flag not set'
    assert getattr(command, 'called', False), message

def test_assert_called_flag():
    """Test that the assert_called_flag function works"""
    class FakeCommand(object):
        def run(self, **kwargs):
            self.called = True
    command = FakeCommand()
    asserted = False
    try:
        assert_called_flag(command)
    except AssertionError:
        asserted = True
    assert asserted
    command.run()
    assert_called_flag(command)

@fudge.test
def test_initialize_command():
    """Test initializing fake command."""
    command = FakeCommand(None)

@raises(AssertionError)
def test_initialize_base_command():
    """Test initializing the base command. Should fail"""
    command = Command()

def test_run():
    """Test when a command's runs with no problems
    
    The run command is wrapped in the execute method
    """
    class FakeCommand(Command):
        name = 'test'
        def run(self, *args, **kwargs):
            self.called = True
    command = FakeCommand()
    assert command.execute('options') == 0
    assert_called_flag(command)

def test_execute_ignores_kwargs():
    """Test when a command's execute method ignores an unknown kwarg"""
    class FakeCommand(Command):
        name = 'test'
        def run(self, *args, **kwargs):
            self.called = True
    command = FakeCommand()
    assert command.execute('options', test='test') == 0
    assert_called_flag(command)

def test_run_with_exception():
    """Test when a command's run method raises an exception."""
    class FakeCommand(Command):
        name = 'test'
        def run(self, *args, **kwargs):
            raise Exception('Forced Error')
    command = FakeCommand()
    assert command.execute('options') == 2

@fudge.patch('virtstrap.basecommand.Project')
def test_project_mixin_loads_project(FakeProject):
    """Test ProjectMixin"""
    class FakeCommand(Command, ProjectMixin):
        name = "test"
    FakeProject.expects('load').with_args('options').returns('proj')
    fake = FakeCommand()
    project = fake.load_project('options')
    assert project == 'proj'

@fudge.patch('virtstrap.basecommand.Project')
def test_project_mixin_loads_project(FakeProject):
    """Test ProjectMixin"""
    class FakeCommand(Command, ProjectMixin):
        name = 'test'
    FakeProject.expects('load').with_args('options').returns('proj')
    fake = FakeCommand()
    project = fake.load_project('options')
    assert project == 'proj'

@fudge.patch('virtstrap.basecommand.Project')
def test_project_command_execute_ignores_kwargs(FakeProject):
    """Test when a project command's execute method ignores an unknown kwarg"""
    (FakeProject.expects('load')
            .with_args('options').returns('proj'))
    class FakeCommand(ProjectCommand):
        name = 'test'
        def run(self, project, options, **kwargs):
            pass
    command = FakeCommand()
    assert command.execute('options', test='test') == 0

@fudge.patch('virtstrap.basecommand.Project')
def test_project_command_execute_injected_project_kwargs(FakeProject):
    """Test when a project instance is injected into command via execute"""
    class FakeCommand(ProjectCommand):
        name = 'test'

        def run(self, project, options, **kwargs):
            self.called = True
            assert project == 'project'

    command = FakeCommand()
    assert command.execute('options', project='project') == 0
    # Assert that called flag is set
    assert_called_flag(command)

@fudge.patch('virtstrap.basecommand.Project')
def test_project_command_runs_with_project(FakeProject):
    """Test ProjectCommand runs correctly"""
    class FakeProjectCommand(ProjectCommand):
        name = 'test'
        def run(self, project, options, **kwargs):
            assert project == 'proj'
    (FakeProject.expects('load')
            .with_args('options').returns('proj'))
    command = FakeProjectCommand()
    return_code = command.execute('options')
    assert return_code == 0

def test_project_command_runs_with_project_not_faked():
    """Test ProjectCommand in a sandbox"""
    class FakeProjectCommand(ProjectCommand):
        name = 'test'
        def run(self, project, options, **kwargs):
            self.called = True
            assert project.name == 'sample_project'
            assert project.env_path().endswith('sample_project/.vs.env')
    from virtstrap.options import create_base_parser
    base_parser = create_base_parser()
    base_options = base_parser.parse_args(args=[])
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    with in_directory(fake_project_sub_directory):
        command = FakeProjectCommand()
        return_code = command.execute(base_options)
        assert return_code == 0
        assert_called_flag(command)

def test_command_creates_template_environment():
    """Test that command creates a template environment"""
    from jinja2 import Environment
    class FakeCommand(Command):
        name = 'test'
        def run(self, *args, **kwargs):
            self.called = True
            assert isinstance(self.template_environment(), Environment)
    command = FakeCommand()
    return_code = command.execute('options')
    assert return_code == 0
    assert_called_flag(command)

def test_command_renders_template_string():
    """Test that command renders a template string"""
    with temp_template_environment(fixture_path('templates')):
        class FakeCommand(Command):
            name = 'test'
            def run(self, *args, **kwargs):
                self.called = True
                assert self.render_template_string(
                        '{{ command.name }}') == 'test'
                assert self.render_template_string(
                        '{{ options }}') == 'options'
                # Test with a user defined context
                assert self.render_template_string(
                        '{{ testvalue }}', testvalue='foo') == 'foo'
        command = FakeCommand()
        return_code = command.execute('options')
        assert return_code == 0
        assert_called_flag(command)

def test_command_renders_template():
    """Test that command renders a template file"""
    with temp_template_environment(fixture_path('templates')):
        class FakeCommand(Command):
            name = 'test'
            def run(self, *args, **kwargs):
                self.called = True
                # Test with the default context
                assert self.render_template(
                        'tests/test_template.sh.jinja') == 'test::options'
                # Test with a user defined context
                assert self.render_template(
                        'tests/test_with_context.sh.jinja', 
                        testvalue='bar') == 'bar'
        command = FakeCommand()
        return_code = command.execute('options')
        assert return_code == 0
        assert_called_flag(command)

@fudge.patch('virtstrap.basecommand.Project')
def test_project_command_renders_template(FakeProject):
    """Test that a project command adds current project to the context"""
    (FakeProject.expects('load')
            .with_args('options').returns('proj'))
    with temp_template_environment(fixture_path('templates')):
        class FakeCommand(ProjectCommand):
            name = 'test'
            def run(self, project, options, **kwargs):
                assert self.render_template_string('{{ project }}') == 'proj'
                assert self.render_template(
                        'tests/test_project_template.sh.jinja') == 'proj'
        command = FakeCommand()
        assert command.execute('options', test='test') == 0
