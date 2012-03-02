"""
Test Options
------------

"""
from virtstrap.options import *

def test_initialize_cli_list():
    l = CLIList()
    assert isinstance(l, list)

def test_cli_list_acts_like_list():
    """Ensure that CLIList still acts like a list"""
    l = CLIList([1,2,3,4])
    assert l[0] == 1
    assert l[1:] == [2,3,4]
    l.append(5)
    assert l == [1,2,3,4,5]
    assert l[-1] == 5

def test_cli_list_converts_to_cli_string():
    l1 = CLIList([1,2,3,4])
    assert str(l1) == '1,2,3,4'
    assert unicode(l1) == u'1,2,3,4'

    l2 = CLIList(['a','b','c','d'])
    assert str(l2) == 'a,b,c,d'
    assert unicode(l2) == u'a,b,c,d'

def test_convert_base_options_to_args():
    base_parser = create_base_parser()
    options = base_parser.parse_args(args=[])
    converted = base_options_to_args(options)
    assert converted == ['--config-file=VEfile', '--log=.virtstrap.log',
            '--profiles=development', '--verbosity=2',
            '--virtstrap-dir=.vs.env']

def test_convert_base_options_to_args_with_multiple_profiles():
    """Check that multiple profiles show up correctly"""
    # This is a regression test.
    base_parser = create_base_parser()
    options = base_parser.parse_args(
            args=['--profiles=development,production'])
    converted = base_options_to_args(options)
    assert converted == ['--config-file=VEfile', '--log=.virtstrap.log',
            '--profiles=development,production', '--verbosity=2',
            '--virtstrap-dir=.vs.env']


    
