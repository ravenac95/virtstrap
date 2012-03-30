"""
virtstrap.tempfiler
~~~~~~~~~~~~~~~~~~~

An extremely simple script that simply creates a temporary file to be used for
communication between virtstrap programs. The reason we're not doing this in
bash or something similar is to make sure this is portable. This also allows
any command to log whatever it wishes to the user while still maintaining 
the correct functions. This is because the communicating programs do not 
listen to stdout. This is mostly useful for communicating with shell scripts.
"""
import tempfile
import sys
import os

def main():
    handle, filename = tempfile.mkstemp()
    os.close(handle)
    sys.stdout.write(filename)
