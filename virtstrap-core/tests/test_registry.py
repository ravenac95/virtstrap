import fudge
from virtstrap.registry import *
from virtstrap.testing import *

def test_initialize_command_registry():
    registry = CommandRegistry()

class TestCommandRegistry(object):
    def setup(self):
        fake_parent = fudge.Fake()
        self.fake_parent = fake_parent
        fake_parent.provides('call_plugins')
        self.registry = CommandRegistry(parent=fake_parent)

    def test_register_a_command(self):
        """Test that a command registers correctly"""
        class FakeCommand(object):
            name = 'test'
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.retrieve('test') == FakeCommand

    @fudge.test
    def test_run_a_command(self):
        """Test that a command runs correctly"""
        from virtstrap.commands import Command
        # Setup fake command instance
        command_args = ('test', 'options')
        class FakeCommand(Command):
            name = 'test'
            called = False
            def run(self, options, **kwargs):
                self.__class__.called = True
                assert options == 'options'

        #register to the registry
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.run(*command_args) == 0
        assert FakeCommand.called

    @fudge.test
    def test_run_a_command_with_fake_kwargs(self):
        """Test that a command runs correctly with fake kwargs"""
        from virtstrap.commands import Command
        # Setup fake command instance
        command_args = ('test', 'options')
        class FakeCommand(Command):
            name = 'test'
            called = False
            def run(self, options, **kwargs):
                self.__class__.called = True
                assert options == 'options'

        #register to the registry
        registry = self.registry
        registry.register(FakeCommand)
        assert registry.run(*command_args, test='test') == 0
        assert FakeCommand.called

    @fudge.test
    def test_list_commands(self):
        com1 = fake_command('com1')
        com2 = fake_command('com2')

        registry = self.registry
        registry.register(com1)
        registry.register(com2)

        assert set(registry.list_commands()) == set(['com1', 'com2'])

def test_initialize_plugin_registry():
    registry = PluginRegistry()

class TestPluginRegistry(object):
    def setup(self):
        self.registry = PluginRegistry()

    def test_run_a_plugin(self):
        from virtstrap.baseplugin import create
        @create('command1', ['event1', 'event2'])
        def handle_command1_events(event, options, **kwargs):
            assert event in ['event1', 'event2']
            options['%s_1' % event] = True
        
        @create('command2', ['event1'])
        def handle_command2_events(event, options, **kwargs):
            assert event in 'event1'
            options['%s_2' % event] = True

        self.registry.register(handle_command1_events)
        self.registry.register(handle_command2_events)
        options = dict(event1_1=False, event2_1=False, event1_2=False)
        self.registry.call_plugins('command1', 'event1', options)
        self.registry.call_plugins('command1', 'event2', options)
        self.registry.call_plugins('command2', 'event1', options)

        assert options['event1_1'], "Plugin was not run for command1, event1"
        assert options['event2_1'], "Plugin was not run for command1, event2"
        assert options['event1_2'], "Plugin was not run for command2, event1"
