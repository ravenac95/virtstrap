"""
Fake PyPI Server
================

Creates a fake pypi so that you can use it for testing
"""
import socket
import os
import time
import shutil
import signal
from contextlib import contextmanager
from subprocess import Popen

@contextmanager
def temp_pip_index(packages_directory):
    """Context manager for a temporary pip index"""
    # Get an unused socket
    temp_socket = socket.socket()
    temp_socket.bind(('', 0))
    port_number = temp_socket.getsockname()[1]

    # Get temporary pip index url
    temp_pip_index = 'http://127.0.0.1:%u/simple/' % port_number
    # Setup the environment variables
    old_pip_index = os.environ.get('PIP_INDEX_URL', None)
    os.environ['PIP_INDEX_URL'] = temp_pip_index
    pypi_server_bin = 'pypi-server'
    dev_null = open(os.devnull, 'w')
    # Run the server
    pypi_process = Popen([pypi_server_bin, '-i',
            '127.0.0.1', '-p', '%u' % port_number, packages_directory], 
            stdout=dev_null, stderr=dev_null)
    try:
        yield temp_pip_index
    finally:
        if not old_pip_index:
            del os.environ['PIP_INDEX_URL']
        else:
            os.environ['PIP_INDEX_URL'] = old_pip_index
        # Kill the server
        pypi_process.terminate()
        # For good measure do it many times.
        pypi_process.kill()
        os.kill(pypi_process.pid, signal.SIGTERM)
