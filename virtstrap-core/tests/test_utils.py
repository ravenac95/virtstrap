from nose.tools import *
from virtstrap.utils import *
from tests import fixture_path

class TestException(Exception):
    pass

def test_import_string():
    """Test import some modules"""
    tests = [
        'virtstrap.commands',
        'virtstrap.options'
    ]
    for string in tests:
        yield import_a_string, string

def import_a_string(string):
    import_string(string)

@raises(ImportStringError)
def test_import_string_fails():
    string = 'virtstrap.thisisanameyouwouldneveruse'
    import_string(string)

def test_in_directory():
    """Test change CWD to a specific directory"""
    basic_project_dir = fixture_path('sample_project')
    with in_directory(basic_project_dir):
        assert basic_project_dir == os.path.abspath('.')
    assert basic_project_dir != os.path.abspath('.')

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
