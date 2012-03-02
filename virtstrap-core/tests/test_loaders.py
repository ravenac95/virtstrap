import fudge
from virtstrap import commands
from virtstrap.testing import *
from virtstrap.loaders import *

def registry_command_names_set():
    command_names = set()
    for command_name, command in commands.registry.commands_iter():
        command_names.add(command_name)
    return command_names

def command_names_set(commands):
    return set(map(lambda a: a.name, commands))


class TestLoader(object):
    def setup(self):
        commands.registry = commands.CommandRegistry()

    def teardown(self):
        commands.registry = None

    @fudge.test
    def test_load(self):
        """Test that the loader uses the collector correctly"""
        collector = fudge.Fake()
        fake_commands = [fake_command('alpha'), 
                fake_command('beta')]
        collector.expects('collect').returns(fake_commands)
        loader = CommandLoader(collectors=[collector])
        loader.load()
        expected = set(['alpha', 'beta'])
        command_names = registry_command_names_set()
        assert command_names == expected
    
    def test_load_nothing(self):
        collector = BuiltinCommandCollector('tests.nocommands')
        loader = CommandLoader(collectors=[collector])
        loader.load()
        expected = set()
        command_names = registry_command_names_set()
        assert command_names == expected

class TestModuleCollectionMixin(object):
    def test_collect_commands_in_module(self):
        mixin = ModuleCollectionMixin()
        class FakeModule(object):
            a = fake_command('alpha')
            b = fake_command('beta')
        expected = set(['alpha', 'beta'])
        commands = mixin.collect_commands_in_module(FakeModule)
        command_names = command_names_set(commands)
        assert command_names == expected

def test_builtin_collector_collect():
    location = 'tests.commands'
    expected = set(['init', 'clean', 'install', 'info'])
    collector = BuiltinCommandCollector(location)
    collected_commands = collector.collect()
    command_names = command_names_set(collected_commands)
    assert command_names == expected

@fudge.patch('pkg_resources.iter_entry_points')
def test_plugin_collector_collect(fake_iter_entry):
    """Collect commands via entry points"""
    class FakeModule(object):
        a = fake_command('alpha')
        b = fake_command('beta')
    entry_point = 'virtstrap.commands'
    (fake_iter_entry.expects_call()
            .with_args(entry_point).returns([FakeModule]))
    expected = set(['alpha', 'beta'])
    collector = PluginCommandCollector(entry_point)
    collected_commands = collector.collect()
    command_names = command_names_set(collected_commands)
    assert command_names == expected
