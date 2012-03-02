"""
virtstrap.commands
------------------

This is the main frontend for the command registry and for the Command 
classes.
"""

from virtstrap.registry import CommandRegistry
# Conveniently provide Command and ProjectCommand
from virtstrap.basecommand import * 

# Global Command Registry Handle
registry = None

def run(*args, **kwargs):
    """Shortcut to the registry's run method"""
    registry.run(*args, **kwargs)
