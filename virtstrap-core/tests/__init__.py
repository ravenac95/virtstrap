import os
import sys

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, '..'))

sys.path.insert(0, PROJECT_DIR)

def fixture_path(file_path=''):
    return os.path.join(TEST_DIR, 'fixture', file_path)
