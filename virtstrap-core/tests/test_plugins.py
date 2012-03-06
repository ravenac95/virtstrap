"""
Test Plugins
------------

"""
from nose.tools import raises
from virtstrap.plugins import Plugin, create

def test_initialize_plugin():
    plugin = Plugin()

@raises(NotImplementedError)
def test_run_plugin():
    plugin = Plugin()
    options = None
    plugin.run('fake_event', options)

def test_fake_plugin():
    class FakePlugin(Plugin):
        name = 'fake'
        was_run = False

        def run(self, event, options, **kwargs):
            assert event == 'fake_event'
            assert options == 'options'
            self.was_run = True

    plugin = FakePlugin()
    plugin.execute('fake_event', 'options')
    assert plugin.was_run, 'Plugin did not make it to run'

def test_create_plugin():
    was_run = False
    @create('command', ['event'])
    def fake_plugin(event, options, **kwargs):
        assert event == 'event'
        options['test'] = True

    options = {'test': False}

    assert fake_plugin.name == 'fake_plugin'
    assert fake_plugin.command == 'command'
    
    fake_plugin.execute('event', options)
    assert options['test'], 'Plugin did not make it to run the function'

