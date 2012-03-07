from __future__ import with_statement
import tempfile
import os
import shutil
from contextlib import contextmanager
from virtstrap.utils import ChangedWorkingDirectory, in_directory

class TempDirectory(object):
    def __init__(self):
        self._temp_directory = None

    def __enter__(self):
        # Make temp directory
        temp_directory = tempfile.mkdtemp()
        # Ensure we have the real path (mostly for OS X)
        temp_directory = os.path.realpath(temp_directory)
        self._temp_directory = temp_directory
        return temp_directory

    def __exit__(self, ex_type, ex_value, traceback):
        # Delete temp directory
        shutil.rmtree(self._temp_directory)

@contextmanager
def in_temp_directory():
    """Context manager for a changing CWD to a temporary directory
    
    This is a tool to create a temporary directory and changes directory
    to the temporary directory.
    """
    with TempDirectory() as temp_dir:
        with ChangedWorkingDirectory(temp_dir):
            yield temp_dir

@contextmanager
def temp_directory():
    """Context manager for a temporary directory

    Creates a temporary directory and deletes once done
    """
    with TempDirectory() as temp_dir:
        yield temp_dir

@contextmanager
def temp_virtualenv(*args, **kwargs):
    import virtualenv
    with in_temp_directory() as temp_dir:
        virtualenv.create_environment(temp_dir, site_packages=False)
        yield temp_dir
