"""
virtstrap.testing.context

Tools for dealing with context managers
"""

class ContextUser(object):
    """Uses context objects without the with statement"""
    def __init__(self, context_manager):
        self._context_manager = context_manager

    def enter(self):
        """Enters the context"""
        return self._context_manager.__enter__()
    
    def exit(self, ex_type=None, ex_value=None, traceback=None):
        """Exits the context"""
        return self._context_manager.__exit__(ex_type, ex_value, traceback)
