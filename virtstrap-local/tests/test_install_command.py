import sys
import os
import fudge
import textwrap
from fudge.patcher import patch_object
from nose.plugins.attrib import attr
from tests import fixture_path
from virtstrap import constants
from virtstrap.testing import *
from virtstrap_local.commands.install import InstallCommand

PACKAGES_DIR = fixture_path('packages')

def test_initialize_command():
    command = InstallCommand()

class SpecialFake(fudge.Fake):
    def __iter__(self):
        return iter(self.__iter_patch__())

def fake_requirements(names):
    requirements = []
    for name in names:
        fake = fudge.Fake(name)
        fake.has_attr(name=name)
        fake.provides('to_pip_str').returns(name)
        requirements.append(fake)
    return requirements

def test_special_fake_works():
    fake = SpecialFake()
    fake.expects('__iter_patch__').returns(fake_requirements(['test1']))
    looped = False
    for req in fake:
        looped = True
        assert req.name == 'test1'
    assert looped, 'Did not iterate correctly'

def pip_requirements(project):
    from subprocess import Popen, PIPE
    proc = Popen([project.bin_path('pip'), 'freeze'], stdout=PIPE)
    stdout, stderr = proc.communicate()
    return stdout.splitlines()


class TestInstallCommand(object):
    def setup(self):
        self.command = InstallCommand()
        self.pip_index_ctx = ContextUser(temp_pip_index(PACKAGES_DIR))
        self.index_url = self.pip_index_ctx.enter()
        self.temp_proj_ctx = ContextUser(temp_project())
        self.project, self.options, self.temp_dir = self.temp_proj_ctx.enter()

        self.old_sys_path = sys.path
        python_version = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        new_path = self.project.env_path(
            'lib/python%s/site-packages' % python_version)
        sys.path.append(new_path)

    def teardown(self):
        sys.path = self.old_sys_path
        self.temp_proj_ctx.exit()
        self.pip_index_ctx.exit()
    
    @attr('slow')
    @hide_subprocess_stdout
    @fudge.test
    def test_run_install(self):
        # Install should process the requirements 
        # and create a requirement_set
        # The requirement_set is then turned into a 
        # string and written to a requirements file to be
        # used by pip and install the requirements
        project = self.project
        options = self.options
        temp_dir = self.temp_dir
        fake_req_set = SpecialFake()
        (project.__patch_method__('process_config_section')
                .returns(fake_req_set))
        
        fake_req_set_iter = fake_requirements(['test1'])
        fake_req_set.expects('__iter_patch__').returns(fake_req_set_iter)
        self.command.run(project, options)
        requirements_file = open(constants.VE_LOCK_FILENAME)
        requirements_data = requirements_file.read()
        assert 'test1==0.2' in requirements_data

    @attr('slow')
    @hide_subprocess_stdout
    @fudge.test
    def test_run_install_multiple_packages(self):
        project = self.project
        options = self.options
        temp_dir = self.temp_dir
        fake_req_set = SpecialFake()
        (project.__patch_method__('process_config_section')
                .returns(fake_req_set))
        
        fake_req_set_iter = fake_requirements(['test1', 'test5'])
        fake_req_set.expects('__iter_patch__').returns(fake_req_set_iter)

        self.command.run(project, options)
        requirements_file = open(constants.VE_LOCK_FILENAME)
        requirements_data = requirements_file.read()
        expected_packages = ['test1==0.2', 'test2==1.3', 
                'test3==0.10.1', 'test5==1.4.3']
        for package in expected_packages:
            assert package in requirements_data

    @attr('slow')
    @hide_subprocess_stdout
    @fudge.test
    def test_run_install_using_lock_file(self):
        project = self.project
        options = self.options
        temp_dir = self.temp_dir
        fake_req_set = SpecialFake()
        (project.__patch_method__('process_config_section')
                .returns(fake_req_set))

        lock_file_path = project.path(constants.VE_LOCK_FILENAME)
        lock_file = open(lock_file_path, 'w')
        lock_file.write(textwrap.dedent("""
            test1 (test1==0.1)
            test2 (test2==1.3)
            test3 (test3==0.10.1)
            test5 (test5==1.4.3)
        """))
        lock_file.close()

        fake_req_set_iter = fake_requirements(['test1', 'test5'])
        fake_req_set.expects('__iter_patch__').returns(fake_req_set_iter)

        self.command.run(project, options)

        pip_packages = pip_requirements(project)
        
        expected_packages = ['test1==0.1', 'test2==1.3', 
                'test3==0.10.1', 'test5==1.4.3']
        for package in expected_packages:
            assert package in pip_packages

class TestInstallCommandOutsideOfDirectory(object):
    def setup(self):
        self.command = InstallCommand()
        self.pip_index_ctx = ContextUser(temp_pip_index(PACKAGES_DIR))
        self.index_url = self.pip_index_ctx.enter()
        self.temp_proj_ctx = ContextUser(temp_project(False))
        self.project, self.options, self.temp_dir = self.temp_proj_ctx.enter()

        self.old_sys_path = sys.path
        python_version = '%d.%d' % (sys.version_info[0], sys.version_info[1])
        new_path = self.project.env_path(
            'lib/python%s/site-packages' % python_version)
        sys.path.append(new_path)

    def teardown(self):
        sys.path = self.old_sys_path
        self.temp_proj_ctx.exit()
        self.pip_index_ctx.exit()

    @attr('slow')
    @hide_subprocess_stdout
    @fudge.test
    def test_run_install_using_lock_file_outside(self):

        project = self.project
        options = self.options
        temp_dir = self.temp_dir
        fake_req_set = SpecialFake()
        (project.__patch_method__('process_config_section')
                .returns(fake_req_set))

        lock_file_path = project.path(constants.VE_LOCK_FILENAME)
        lock_file = open(lock_file_path, 'w')
        lock_file.write(textwrap.dedent("""
            test1 (test1==0.1)
            test2 (test2==1.3)
            test3 (test3==0.10.1)
            test5 (test5==1.4.3)
        """))
        lock_file.close()
        fake_req_set_iter = fake_requirements(['test1', 'test5'])
        fake_req_set.expects('__iter_patch__').returns(fake_req_set_iter)

        self.command.run(project, options)

        pip_packages = pip_requirements(project)
        
        expected_packages = ['test1==0.1', 'test2==1.3', 
                'test3==0.10.1', 'test5==1.4.3']
        for package in expected_packages:
            assert package in pip_packages
