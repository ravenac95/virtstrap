"""
virtstrap.constants
-------------------

This module contains constants that are used throughout the application. These
should not change during runtime under any circumstances.
"""

# The virtstrap environment directory (this is where virtualenv is installed)
VIRTSTRAP_DIR = '.vs.env'

# The default runtime log file. This is created in the CWD. This is for
# handling errors and bug reports and such
LOG_FILE = '.virtstrap.log'

# This is a filename for the quickactivate script used as a shortcut to
# activating a projects virtstrap environment
QUICK_ACTIVATE_FILENAME = 'quickactivate'

# Config file name
VE_FILENAME = 'VEfile'

# Config lock file name
VE_LOCK_FILENAME = 'VEfile.lock'

# Default Profile
DEFAULT_PROFILES = ['development']

# BIN NAME FOR VIRTSTRAP WHEN INSIDE A PROJECT
PROJECT_VIRTSTRAP_BIN_NAME = 'virtstrap-local'
