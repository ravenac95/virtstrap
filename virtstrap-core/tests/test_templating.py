"""
Test Templating
---------------
"""
from jinja2 import Environment
from virtstrap.templating import environment, temp_template_environment
from tests import fixture_path

def test_get_environment():
    env = environment()
    assert isinstance(env, Environment)

def test_environment_get_template():
    env = environment()
    template = env.get_template('init/activate.sh.jinja')

def test_test_environment_context():
    from jinja2 import FileSystemLoader
    templates_path = fixture_path('templates')
    with temp_template_environment(templates_path):
        env = environment()
        env.get_template('tests/test_template.sh.jinja')
    env = environment()
    template = env.get_template('init/activate.sh.jinja')
