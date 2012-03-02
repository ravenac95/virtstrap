"""
Test VirtstrapConfig
====================
"""
import fudge
from nose.tools import *
from tests import fixture_path
from virtstrap.config import VirtstrapConfig, ConfigurationError

FAKE_CONFIG = """
list_section:
  - value1
  - value2
  - value3

kv_section:
  key1: value1

data1: value1

---
profile: profile1

list_section:
  - value4

kv_section:
  key2: value2

data1: value2

---
profile: profile2

list_section:
  - value5

kv_section:
  key1: override1

data1: value3
"""

BAD_CONFIG = """
list_section:
  - value1

---
profile: profile1

list_section:
  - value4

---
profile: profile1

list_section:
  - value5
"""

def create_fake_config():
    return VirtstrapConfig.from_string(FAKE_CONFIG)

def test_load_config_from_string():
    """Test that we can load a config at all"""
    config = create_fake_config()
    assert isinstance(config, VirtstrapConfig)

def test_load_from_file():
    """Load configuration from a file"""
    config = VirtstrapConfig.from_file(fixture_path('test.yml'))
    assert isinstance(config, VirtstrapConfig)

def test_load_from_file_does_not_exist():
    """Load a configuration file even if it doesn't exist"""
    config = VirtstrapConfig.from_file(fixture_path('i_do_not_exist____.yml'))
    assert isinstance(config, VirtstrapConfig)

@raises(ConfigurationError)
def test_load_config_from_bad_string():
    """Test loading of a bad configuration"""
    config = VirtstrapConfig.from_string(BAD_CONFIG)

class TestVirtstrapConfig(object):
    def setup(self):
        self.config = create_fake_config()

    def section_data_for_sections(self, section, profiles, expected_data):
        """Test section data compilation"""
        self.config.set_profiles(profiles)
        section_data = self.config.section(section)
        assert section_data == expected_data

    def test_collect_multiple_list_sections(self):
        """Generates various tests for list-based sections"""
        profiles = [
            [],
            ['profile1'],
            ['profile2'],
            ['profile1', 'profile2'],
        ]
        expected_values = [
            ['value1', 'value2', 'value3'],
            ['value1', 'value2', 'value3', 'value4'],
            ['value1', 'value2', 'value3', 'value5'],
            ['value1', 'value2', 'value3', 'value4', 'value5'],
        ]
        tests = zip(profiles, expected_values)
        for profiles, expected in tests:
            yield (self.section_data_for_sections, 'list_section', profiles,
                expected)

    def test_collect_multiple_kv_sections(self):
        """Generates various tests for key value based sections"""
        profiles = [
            [],
            ['profile1'],
            ['profile2'],
            ['profile1', 'profile2'],
        ]
        expected_values = [
            {'key1': 'value1'},
            {'key1': 'value1', 'key2': 'value2'},
            {'key1': 'override1'},
            {'key1': 'override1', 'key2': 'value2'},
        ]
        tests = zip(profiles, expected_values)
        for profiles, expected in tests:
            yield (self.section_data_for_sections, 'kv_section', profiles,
                expected)

    def test_collect_multiple_data_sections(self):
        """Generates various tests for data based sections"""
        profiles = [
            [],
            ['profile1'],
            ['profile2'],
            ['profile1', 'profile2'],
        ]
        expected_values = [
            'value1',
            'value2',
            'value3',
            'value3',
        ]
        tests = zip(profiles, expected_values)
        for profiles, expected in tests:
            yield (self.section_data_for_sections, "data1", profiles,
                expected)

    @fudge.test
    def test_process_section(self):
        process_function = fudge.Fake()
        process_function = (process_function.expects_call()
                .with_args(['value1', 'value2', 'value3'])
                .returns('fake_return'))
        self.config.process_section('list_section', process_function)
        assert 'fake_return' == self.config.processed_section('list_section')

    @fudge.test
    def test_process_section_using_multiple_profiles(self):
        process_function = fudge.Fake()
        process_function = (process_function.expects_call()
                .with_args(['value1', 'value2', 'value3', 'value4', 'value5'])
                .returns('fake_return'))
        self.config.set_profiles(['profile1', 'profile2'])
        self.config.process_section('list_section', process_function)
        assert 'fake_return' == self.config.processed_section('list_section')
