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

def plugin_names_set(plugins):
    return set(map(lambda a: a.name, plugins))

class TestLoader(object):
    def setup(self):
        commands.registry = commands.Registry()

    def teardown(self):
        commands.registry = None

    @fudge.test
    def test_load(self):
        """Test that the loader uses the collector correctly"""
        collector = fudge.Fake()
        fake_commands = [fake_command('alpha'), 
                fake_command('beta')]
        collector.expects('collect').returns((fake_commands, []))
        loader = CommandLoader(collectors=[collector])
        loader.load()
        expected = set(['alpha', 'beta'])
        command_names = registry_command_names_set()
        assert command_names == expected
    
    def test_load_nothing(self):
        collector = BuiltinCollector('tests.nocommands')
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
            c = fake_plugin('charlie')
            d = fake_plugin('delta')
        expected_commands = set(['alpha', 'beta'])
        expected_plugins = set(['charlie', 'delta'])
        commands, plugins = mixin.collect_in_module(FakeModule)
        command_names = command_names_set(commands)
        plugin_names = plugin_names_set(plugins)
        assert command_names == expected_commands
        assert plugin_names == expected_plugins

def test_builtin_collector_collect():
    location = 'tests.commands'
    expected = set(['init', 'clean', 'install', 'info'])
    collector = BuiltinCollector(location)
    collected_commands, collected_plugins = collector.collect()
    command_names = command_names_set(collected_commands)
    assert command_names == expected
    assert collected_plugins == []

@fudge.patch('pkg_resources.iter_entry_points')
def test_plugin_collector_collect(fake_iter_entry):
    """Collect commands via entry points"""
    class FakeEntryPointModule(object):
        a = fake_command('alpha')
        b = fake_command('beta')
        c = fake_plugin('charlie')
        d = fake_plugin('delta')
        
        @classmethod
        def load(cls): # Fake the entry point
            return cls
    entry_point = 'virtstrap.commands'
    (fake_iter_entry.expects_call()
            .with_args(entry_point).returns([FakeEntryPointModule]))
    expected_commands = set(['alpha', 'beta'])
    expected_plugins = set(['charlie', 'delta'])
    collector = PluginCollector(entry_point)
    collected_commands, collected_plugins = collector.collect()
    command_names = command_names_set(collected_commands)
    plugin_names = plugin_names_set(collected_plugins)
    command_names = command_names_set(collected_commands)
    assert command_names == expected_commands
    assert plugin_names == expected_plugins
