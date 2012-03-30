"""
Test Templating
---------------
"""
import fudge
from nose.tools import raises
from jinja2 import Environment
from virtstrap.templating import *
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

def test_tempita_environment():
    env = TempitaEnvironment()

class TestTempitaEnvironment(object):
    def setup(self):
        self.env = TempitaEnvironment()

    def setup_loaders(self):
        fake_loader = fudge.Fake()
        self.env.add_loader(fake_loader)
        return fake_loader

    
    @fudge.test
    def test_add_loader(self):
        fake_loader = self.setup_loaders()
        (fake_loader.expects('get_template').with_args('name', self.env)
                .returns('sometemplate'))
        self.env.add_loader(fake_loader)
        template = self.env.get_template('name')
        assert template == 'sometemplate'
    
    @raises(TemplateDoesNotExist)
    @fudge.test
    def test_get_template_fails(self):
        fake_loader = self.setup_loaders()
        (fake_loader.expects('get_template').with_args('name2', self.env)
                .returns(None))
        self.env.get_template('name2')

def test_template():
    template = Template('template')

class TestTempitaTemplate(object):
    def setup(self):
        fake_tempita_template = fudge.Fake()
        self.template = Template(fake_tempita_template)
        self.fake_tempita_template = fake_tempita_template
    
    @fudge.test
    def test_render(self):
        context = dict(a='hello')
        (self.fake_tempita_template.expects('substitute')
            .with_args(context)
            .returns('somerendering'))
        assert self.template.render(context) == 'somerendering'

@raises(NotImplementedError)
def test_loader():
    loader = TemplateLoader()
    template = loader.get_template('tests/test_template.tmpl', None)
    #assert template.render(dict(name="hello")) == "hello"

def fake_environment():
    fake_env = fudge.Fake('TempitaEnvironment')
    fake_env.provides('get_template').returns('template')
    fake_env.provides('get_tempita_template').returns('template')
    return fake_env

@fudge.patch('virtstrap.templating.Template')
def test_loader_load_template_file(fake_template_class):
    loader = TemplateLoader()
    fake_env = fudge.Fake()
    fake_env.has_attr(get_template='something')
    fake_template_class.expects('from_filename').returns('template')
    template = loader.load_template_file('path', fake_env)
    assert template == 'template'

def test_file_system_loader():
    loader = FileSystemLoader(fixture_path('templates'))
    fake_env = fake_environment()
    template = loader.get_template('tests/test_template.tmpl', fake_env)
    assert template is not None
    
class TestHighLevelTempitaTemplate(object):
    def setup(self):
        template_path = fixture_path('templates')
        loaders = [FileSystemLoader(template_path)]
        self.env = TempitaEnvironment(loaders=loaders)

    def test_render_template(self):
        template = self.env.get_template('tests/test_template.tmpl')
        rendered = template.render(dict(name="hello")).strip()
        assert rendered == 'hello'

    def test_render_inheriting_template(self):
        template = self.env.get_template('tests/test_child.tmpl')
        rendered = template.render(dict(parent_name="parent", 
            name="child")).strip()
        assert rendered == 'parent\nchild'
