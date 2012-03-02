import os
import urllib2
from nose.tools import raises
from nose.plugins.attrib import attr
from virtstrap import constants
from virtstrap.testing import *
from tests import fixture_path

def test_in_directory():
    """Test change CWD to a specific directory"""
    basic_project_dir = fixture_path('sample_project')
    with in_directory(basic_project_dir):
        assert basic_project_dir == os.path.abspath('.')
    assert basic_project_dir != os.path.abspath('.')

def test_temp_directory():
    """Test temp directory correctly deletes"""
    with temp_directory() as temp_dir:
        pass
    assert os.path.exists(temp_dir) == False

def test_in_temp_directory():
    """Test CWD to temp directory"""
    with in_temp_directory() as temp_directory:
        assert os.getcwd() == temp_directory
    assert os.path.exists(temp_directory) == False

def test_in_temp_directory_write_file():
    """Test CWD to temp directory and create file there"""
    with in_temp_directory() as temp_directory:
        # Create a test file in the directory
        test_filename = "test_file.txt"
        test_file = open(test_filename, "w")
        # Put some random data in it
        random_data = random_string(15)
        test_file.write(random_data)
        test_file.close()
        # Attempt to open the file using the full path to the temp directory 
        test_file_path = os.path.join(temp_directory, test_filename)
        # Verify contents
        verify_file = open(test_file_path)
        verify_data = verify_file.read()
        assert random_data == verify_data

@attr('slow')
def test_fake_pypi():
    packages_directory = 'tests/fixture/packages'
    with temp_pip_index(packages_directory) as index_url:
        urllib2.urlopen(index_url)

@hide_subprocess_stdout
def test_subprocess_popen_proxy():
    import subprocess
    process = subprocess.Popen(['echo', 'hello'])
    process.wait()
    process_stdout = getattr(process, 'stdout', None)
    output = process_stdout.read()
    assert process_stdout is not None
    assert output == 'hello\n'
    
def test_dict_to_object():
    obj = dict_to_object(dict(a=1,b=2))
    assert obj.a == 1
    assert obj.b == 2

@attr('slow')
def test_temp_virtualenv():
    with temp_virtualenv() as temp_env_dir:
        assert os.path.exists(os.path.join(temp_env_dir, 'bin/python'))
    assert not os.path.exists(os.path.join(temp_env_dir, 'bin/python'))

class TestException(Exception):
    pass

def test_temp_directory_raises_error():
    raised_error = False
    try:
        with temp_directory() as temp_dir:
            raise TestException()
    except TestException:
        raised_error = True
    assert raised_error
    assert not os.path.exists(temp_dir)

def test_in_directory_raises_error():
    raised_error = False
    original_working_dir = os.getcwd()
    basic_project_dir = fixture_path('sample_project')
    try:
        with in_directory(basic_project_dir):
            raise TestException()
    except TestException:
        raised_error = True
    assert raised_error
    assert os.getcwd() == original_working_dir

@attr('slow')
@fudge.test
def test_temp_project():
    from virtstrap.project import Project
    with temp_project() as info:
        project, options, temp_dir = info
        assert os.path.exists(temp_dir)
        assert options.virtstrap_dir == constants.VIRTSTRAP_DIR
        assert options.project_dir == temp_dir
        assert project.path() == temp_dir
        # Make sure virtualenv did it's job
        assert os.path.exists(project.bin_path('pip'))
        assert isinstance(project, Project)
        assert isinstance(project, FakeProject)
        # Test the FakeProject
        project.__patch_method__('bin_path').returns('hello')
        assert project.bin_path() == 'hello'
    assert not os.path.exists(temp_dir)

def test_context_user():
    from contextlib import contextmanager
    test_dict = dict(value='before')
    @contextmanager
    def test_context(test_dict):
        test_dict['value'] = 'during'
        yield 'test'
        test_dict['value'] = 'after'
    ctx = ContextUser(test_context(test_dict))
    assert test_dict['value'] == 'before'
    ctx.enter()
    assert test_dict['value'] == 'during'
    ctx.exit()
    assert test_dict['value'] == 'after'


@fudge.test
def test_shunt_mixin():
    """Create an object with the ShuntMixin"""
    class FakeClass(ShuntMixin):
        def my_method(self):
            return "before-shunt"

    obj = FakeClass()
    assert obj.my_method() == 'before-shunt'

    obj.__patch_method__('my_method').returns('after-shunt')
    assert obj.my_method() == 'after-shunt'

@raises(AssertionError)
@fudge.test
def test_shunt_mixin_raises_error():
    class FakeClass(ShuntMixin):
        def my_method(self):
            return "before-shunt"

    obj = FakeClass()
    obj.__patch_method__('my_method').with_args('test')
    obj.my_method()


@fudge.test
def test_shunt_mixin_has_no_expectation_on_patch():
    class FakeClass(ShuntMixin):
        def my_method(self):
            return "before-shunt"

    obj = FakeClass()
    (obj.__patch_method__('my_method', expects_call=False).returns('test')
                    .next_call().with_args('hello').returns('world'))
    assert obj.my_method() == 'test'

@fudge.test
def test_shunt_class_factory_method():
    class FakeClass(object):
        def my_method(self):
            return "before-shunt"
    ShuntClass = shunt_class(FakeClass)
    obj = ShuntClass()
    assert obj.my_method() == 'before-shunt'

    obj.__patch_method__('my_method').returns('after-shunt')
    assert obj.my_method() == 'after-shunt'

def test_fake_command():
    FakeCommand = fake_command('init')
    assert FakeCommand.name == 'init'
