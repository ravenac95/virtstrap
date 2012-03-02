from __future__ import with_statement
import tempfile
import os
import shutil
import virtualenv
from contextlib import contextmanager

class ChangedWorkingDirectory(object):
    def __init__(self, directory):
        self._directory = directory
        self._original_directory = os.getcwd()

    def __enter__(self):
        # Change the directory to the new cwd
        directory = self._directory
        # Change to the new directory
        os.chdir(directory)
        # Return the directory
        return directory

    def __exit__(self, ex_type, ex_value, traceback):
        # Return back to normal
        os.chdir(self._original_directory)

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
def in_directory(directory):
    """Context manager for changing CWD to a directory

    Don't use this if you plan on writing files to the directory.
    This does not delete anything. It is purely to change the CWD
    """
    with ChangedWorkingDirectory(directory) as directory:
        yield directory

@contextmanager
def temp_virtualenv(*args, **kwargs):
    with in_temp_directory() as temp_dir:
        virtualenv.create_environment(temp_dir, site_packages=False)
        yield temp_dir
