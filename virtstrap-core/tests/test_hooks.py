"""
Test Plugins
------------

"""
from nose.tools import raises
from virtstrap.hooks import Hook, create

def test_initialize_Hook():
    hook = Hook()

@raises(NotImplementedError)
def test_run_hook():
    hook = Hook()
    options = None
    hook.run('fake_event', options)

def test_fake_hook():
    class FakeHook(Hook):
        name = 'fake'
        was_run = False

        def run(self, event, options, **kwargs):
            assert event == 'fake_event'
            assert options == 'options'
            self.was_run = True

    hook = FakeHook()
    hook.execute('fake_event', 'options')
    assert hook.was_run, 'Hook did not make it to run'

def test_create_hook():
    was_run = False
    @create('command', ['event'])
    def fake_hook(event, options, **kwargs):
        assert event == 'event'
        options['test'] = True

    options = {'test': False}

    assert fake_hook.name == 'fake_hook'
    assert fake_hook.command == 'command'
    
    fake_hook.execute('event', options)
    assert options['test'], 'Hook did not make it to run the function'
