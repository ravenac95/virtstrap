"""
Test project
------------
"""
import fudge
from fudge.inspector import arg
from fudge.patcher import patch_object
from nose.tools import raises
from tests import fixture_path
from virtstrap.testing import *
from virtstrap.project import *
from virtstrap.options import create_base_parser

def test_initialize_project():
    project = Project()

@fudge.test
def test_project_seeks_project_path():
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    base_parser = create_base_parser()
    base_options = base_parser.parse_args(args=[])
    with in_directory(fake_project_sub_directory):
        project = Project.load(base_options)
        assert project.path() == fixture_path('sample_project')
        assert project.name == 'sample_project'

class BaseProjectTest(object):
    """This handles some common boilerplate between project tests"""
    def base_setup(self, option_overrides):
        # Create a fake VirtstrapConfig
        config = fudge.Fake()
        config.provides('from_file').returns(config)
        self.config = (config.provides('process_section')
                .with_args('project_name', arg.any())
                .returns('projdir'))
        # Patch VirtstrapConfig
        self.config_patch = patch_object('virtstrap.project', 
                'VirtstrapConfig', config)
        base_parser = create_base_parser()
        options = base_parser.parse_args(args=[])
        # Add any overrides
        for name, override in option_overrides.iteritems():
            setattr(options, name, override)
        self._options = options
        self._project = None
    
    @property
    def project(self):
        """Lazy Load the project"""
        project = self._project
        if not project:
            # Only load it once
            self._project = Project.load(self._options)
            project = self._project
        return project

    def teardown(self):
        # Restore to state before patching
        self.config_patch.restore()

class TestProjectAllDirectoriesDefined(BaseProjectTest):
    def setup(self):
        option_overrides = dict(virtstrap_dir='/vsdir', 
            project_dir='/projdir')
        self.base_setup(option_overrides)

    def test_get_project_name(self):
        """Test that the project name is found"""
        project = self.project
        assert project.name == 'projdir'

    def test_project_path(self):
        project = self.project
        assert project.path('a') == '/projdir/a'
        assert project.path('a', 'b') == '/projdir/a/b'

    def test_bin_path(self):
        project = self.project
        assert project.bin_path('a') == '/vsdir/bin/a'
        assert project.bin_path('a', 'b') == '/vsdir/bin/a/b'

    def test_env_path(self):
        project = self.project
        assert project.env_path('a') == '/vsdir/a'
        assert project.env_path('a', 'b') == '/vsdir/a/b'

class TestProjectOnlyProjectDirectoryDefined(BaseProjectTest):
    def setup(self):
        self.base_setup(dict(project_dir='/projdir'))
    
    def test_project_path(self):
        project = self.project
        assert project.path('a') == '/projdir/a'
        assert project.path('a', 'b') == '/projdir/a/b'

    def test_env_path(self):
        project = self.project
        assert project.env_path('a') == '/projdir/.vs.env/a'
        assert project.env_path('a', 'b') == '/projdir/.vs.env/a/b'

    def test_bin_path(self):
        project = self.project
        assert project.bin_path('a') == '/projdir/.vs.env/bin/a'
        assert project.bin_path('a', 'b') == '/projdir/.vs.env/bin/a/b'

class TestProjectGeneral(BaseProjectTest):
    """General Tests for Project"""
    def setup(self):
        # this is necessary
        self.base_setup(dict(project_dir='/projdir'))
    
    @fudge.test
    def test_process_config_section(self):
        (self.config.expects('process_section')
                .with_args('section', 'f')
                .returns('processed'))
        self.project.process_config_section('section', 'f')

    @fudge.test
    def test_access_config_from_project(self):
        (self.config.expects('processed')
                .with_args('test')
                .returns('test_data'))
        assert self.project.config('test') == 'test_data'

    @fudge.patch('virtstrap.project.call_subprocess')
    def test_call_bin(self, fake_call_subprocess):
        """Test that project can call a bin"""
        (fake_call_subprocess.expects_call()
            .with_args(['/projdir/.vs.env/bin/cmd', 'arg1', 'arg2'])
            .next_call()
            .with_args(['/projdir/.vs.env/bin/cmd', 'arg1'], show_stdout=False)
            )
        project = self.project
        project.call_bin('cmd', ['arg1', 'arg2'])
        project.call_bin('cmd', ['arg1'], show_stdout=False)

class TestProjectOnlyProjectDirectoryRelativelyDefined(BaseProjectTest):
    def test_project_path(self):
        with in_temp_directory() as temp_dir:
            self.base_setup(dict(project_dir='./projdir'))
            project = self.project
            print project.path('a')
            assert project.path('a').startswith(temp_dir)
            assert project.path('a').endswith('/projdir/a')
            assert project.path('a', 'b').endswith('/projdir/a/b')

def test_process_project_name():
    name_processor = ProjectNameProcessor('/projdir/')
    assert 'projdir' == name_processor(None)
    assert 'project_dir' == name_processor('project_dir')
    
def test_find_project_directory_from_lev2():
    fake_project_sub_directory = fixture_path('sample_project/lev1/lev2')
    with in_directory(fake_project_sub_directory):
        project_dir = find_project_dir()
        assert project_dir == fixture_path('sample_project')

def test_find_project_directory_from_lev1():
    fake_project_sub_directory = fixture_path('sample_project/lev1')
    with in_directory(fake_project_sub_directory):
        project_dir = find_project_dir()
        assert project_dir == fixture_path('sample_project')

def test_find_project_directory_from_sample_project():
    fake_project_sub_directory = fixture_path('sample_project')
    with in_directory(fake_project_sub_directory):
        project_dir = find_project_dir()
        assert project_dir == fixture_path('sample_project')

@raises(NoProjectFound)
def test_find_project_directory_does_not_exist():
    """Test that find_project_dir raises an error when no project is found"""
    with in_temp_directory() as temp_directory:
        project_dir = find_project_dir()
