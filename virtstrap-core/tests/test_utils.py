from nose.tools import *
from virtstrap.utils import *

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
