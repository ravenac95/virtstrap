from cStringIO import StringIO
import textwrap
import fudge
from nose.tools import raises
from virtstrap.exceptions import RequirementsConfigError
from virtstrap.requirements import *

def test_initialize_processor():
    req_set = RequirementSet()

def test_initialize_from_data():
    req_set = RequirementSet.from_config_data([])
    assert isinstance(req_set, RequirementSet)

class TestRequirementSet(object):
    def test_set_to_pip_str(self):
        # Define a requirements list
        requirements_list = [
            'ipython',
            {'werkzeug': '==0.8'},
            {'requests': '>=0.8'},
            {'jinja2': [
                'git+https://something.com/mitsuhiko/jinja2.git',
                {'editable': True},
            ]},
        ]
        # Define the expected created file
        expected_string = textwrap.dedent("""
            ipython
            werkzeug==0.8
            requests>=0.8
            -e git+https://something.com/mitsuhiko/jinja2.git#egg=jinja2
        """).strip()
        req_set = RequirementSet.from_config_data(requirements_list)
        pip_str = req_set.to_pip_str()
        assert pip_str == expected_string

    @raises(RequirementsConfigError)
    def test_badly_configured_requirements(self):
        """Test that an error is thrown when there is a bad requirement"""
        requirements_list = [
            {'somereq': 'version', 'other': 'version'},
        ]
        req_set = RequirementSet.from_config_data(requirements_list)
        req_set.to_pip_str()

    def test_requirement_set_as_boolean(self):
        req_set = RequirementSet.from_config_data(None)
        assert not req_set

    def test_iterate_requirements_set(self):
        requirements_list = [
            'ipython',
            {'werkzeug': '==0.8'},
            {'requests': '>=0.8'},
            {'jinja2': [
                'git+https://something.com/mitsuhiko/jinja2.git',
                {'editable': True},
            ]},
        ]
        expected_names = ['ipython', 'werkzeug', 'requests', 'jinja2']
        req_set = RequirementSet.from_config_data(requirements_list)
        looped = False
        for requirement in req_set:
            looped = True
            assert requirement.name in expected_names
        assert looped, 'RequirementSet did not iterate at all'

class TestRequirementsProcessor(object):
    def setup(self):
        # RequirementsProcessor uses a dictionary of
        # factory methods to create different types of 
        # Requirement objects from the raw data
        self.fake_requirement_types = fudge.Fake()
        self.processor = RequirementsProcessor(
                requirement_types=self.fake_requirement_types)

    def add_req_expectation(self, type_name, args, kwargs, return_value):
        fake_requirement_type = fudge.Fake()
        fake_requirement_type = (fake_requirement_type.expects_call()
                .with_args(*args, **kwargs)
                .returns(return_value))
        temp = (self.fake_requirement_types.expects('get')
                .with_args(type_name)
                .returns(fake_requirement_type))

    @fudge.test
    def test_process_basic_requirement(self):
        self.add_req_expectation('basic', ['tester'], {}, 'fake_return')

        # Set the requirements list
        raw_requirements_list = [
            'tester',
        ]
        requirements = self.processor.to_requirements(raw_requirements_list)
        assert requirements == ['fake_return']

    @fudge.test
    def test_process_basic_requirement_with_spec(self):
        self.add_req_expectation('basic', ['tester', '==1.4'], 
                {}, 'fake_return')

        raw_requirements_list = [
            {'tester': '==1.4'},
        ]
        requirements = self.processor.to_requirements(raw_requirements_list)
        assert requirements == ['fake_return']

    @fudge.test
    def test_process_vcs_requirement(self):
        self.add_req_expectation('vcs', 
                ['tester', 'git+http://something.com/something.git'], 
                {}, 'fake_return')

        raw_requirements_list = [
            {'tester': 'git+http://something.com/something.git'},
        ]
        requirements = self.processor.to_requirements(raw_requirements_list)
        assert requirements == ['fake_return']
    
    @fudge.test
    def test_process_url_requirement(self):
        self.add_req_expectation('url', 
                ['tester', 'http://something.com/something.git'], 
                {}, 'fake_return')

        raw_requirements_list = [
            {'tester': 'http://something.com/something.git'},
        ]
        requirements = self.processor.to_requirements(raw_requirements_list)
        assert requirements == ['fake_return']

    @raises(RequirementsConfigError)
    def test_bad_requirement(self):
        bad_requirements_list = [
            1, #only strings are accepted. this will throw an error
        ]
        requirements = self.processor.to_requirements(bad_requirements_list)

    @raises(RequirementsConfigError)
    def test_bad_requirement_multiple_keys(self):
        bad_requirements_list = [
            {'key1': 'value', 'key2': 'value'},
        ]
        requirements = self.processor.to_requirements(bad_requirements_list)


def test_initialize_requirement_object():
    requirement = Requirement('somename')
    
def test_requirement_to_pip_string():
    requirement = Requirement('test')
    assert requirement.to_pip_str() == 'test'

def test_requirement_to_pip_string_with_version():
    requirement = Requirement('test', version='==0.9')
    assert requirement.to_pip_str() == 'test==0.9'

def test_requirement_to_pip_string_with_multiple_version_specs():
    requirement = Requirement('test', version='>=0.9,<1.5')
    assert requirement.to_pip_str() == 'test>=0.9,<1.5'

def test_vcs_requirement_to_pip_string():
    requirement = VCSRequirement('test', 'git+http://test.com/')
    assert requirement.to_pip_str() == 'git+http://test.com/#egg=test'

def test_vcs_requirement_to_pip_string_with_editable_flag():
    requirement = VCSRequirement('test', 'git+http://test.com/', editable=True)
    assert requirement.to_pip_str() == '-e git+http://test.com/#egg=test'

def test_vcs_requirement_to_pip_string_with_at_option():
    """Test that you can specify a tag, version, or commit"""
    requirement = VCSRequirement('test', 'git+http://test.com/', at="v1.0", 
            editable=True)
    assert requirement.to_pip_str() == '-e git+http://test.com/@v1.0#egg=test'

def test_url_requirement_to_pip_string():
    requirement = VCSRequirement('test', 'git+http://test.com/')
    assert requirement.to_pip_str() == 'git+http://test.com/#egg=test'
