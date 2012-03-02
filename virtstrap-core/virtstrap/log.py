"""
virtstrap.log
-------------

Provides a central logging facility. It is used to record log info
and report both to a log file and stdout
"""
import sys
import os
import logging
import traceback
from virtstrap import constants

CLINT_AVAILABLE = True
try:
    from clint.textui import puts, colored
except:
    # Clint is still not stable enough yet to just import with so much
    # trust, but I really like colored output. So we'll give it a shot
    # and if it doesn't work we will just do something else.
    CLINT_AVAILABLE = False

def get_logging_level(level):
    logging_level = None
    if isinstance(level, (str, unicode)):
        level = level.upper()
        try:
            logging_level = getattr(logging, level.upper())
        except AttributeError:
            raise AttributeError('Tried to grab logging level "%s"'
                    ' but it does not exist' % level)
    elif isinstance(level, int):
        # Do nothing
        logging_level = level
    else:
        raise TypeError('Invalid logging level. Must be string or int %s'
                % str(level))
    return logging_level
            
class VirtstrapLogger(object):
    """Custom logger for use with virtstrap
    
    It'll allow the logger to store logged data before a log file is setup. It
    is meant to be used globally.
    """
    def __init__(self):
        self._handlers = []
        self._log_lines = [] #storage before any handlers appear

    def add_handler(self, handler):
        self._handlers.append(handler)
        log_lines = self._log_lines
        for level, message in log_lines:
            self.log(level, message, new_line=False)
        self._log_lines = []

    def debug(self, message, **kwargs):
        self.log('debug', message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log('error', message, **kwargs)
    
    def info(self, message, **kwargs):
        self.log('info', message, **kwargs)
    
    def warning(self, message, **kwargs):
        self.log('warning', message, **kwargs)
    
    def critical(self, message, **kwargs):
        self.log('critical', message, **kwargs)

    def exception(self, message, **kwargs):
        exception_str = self._get_exception_str()
        self.log('error', '%s\n%s' % (message, exception_str))

    def debug_exception(self, message, **kwargs):
        """Stores exception except using the debug level"""
        exception_str = self._get_exception_str()
        self.log('debug', '%s\n%s' % (message, exception_str))
    
    def _get_exception_str(self):
        exception_info = sys.exc_info()
        exception_lines = traceback.format_exception(*exception_info)
        exception_str = ''.join(exception_lines)
        return exception_str

    def log(self, level, message, new_line=True):
        if new_line:
            message = "%s\n" % message
        handlers = self._handlers
        if not handlers:
            self._log_lines.append((level, message))
        else:
            for handler in handlers:
                handler.log(level, message)

class VirtstrapLogHandler(object):
    def __init__(self, level='debug'):
        self._level = get_logging_level(level)

    def set_level(self, level):
        self._level = get_logging_level(level)

    def log(self, level, message):
        current_level = get_logging_level(level)
        if current_level >= self._level:
            self.emit(level, message)

    def emit(self, level, message):
        raise NotImplementedError('Please implement an emit method')

class ConsoleLogHandler(VirtstrapLogHandler):
    def emit(self, level, message):
        sys.stdout.write(message)

class ColoredConsoleLogHandler(VirtstrapLogHandler):
    level_colors = {
        "DEBUG": "green",
        "INFO": "black",
        "WARNING": "yellow",
        "CRITICAL": "purple",
        "ERROR": "red",
        "EXCEPTION": "red",
    }
    def emit(self, level, output):
        color = self.level_colors.get(level, "black")
        colored_function = getattr(colored, color, lambda text: text)
        colored_output = colored_function(output)
        puts(colored_output)

class FileLogHandler(VirtstrapLogHandler):
    """File Log Handler that uses built in logging to log"""
    def __init__(self, filename):
        self._file = open(filename, 'a')

    def emit(self, level, message):
        self._file.write(message)

class VirtstrapConsoleLogHandler(logging.Handler):
    def __init__(self, outputter):
        self._outputter = outputter
        logging.Handler.__init__(self)

    def emit(self, record):
        outputter = self._outputter 
        output_string = self.format(record)
        outputter.write(output_string, record.levelname)

class ConsoleLogOutputter(object):
    def write(self, output, level):
        print(output)

class ColoredConsoleLogOutputter(ConsoleLogOutputter):
    level_colors = {
        "DEBUG": "green",
        "INFO": "black",
        "WARNING": "yellow",
        "CRITICAL": "purple",
        "ERROR": "red",
        "EXCEPTION": "red",
    }
    def write(self, output, level):
        color = self.level_colors.get(level, "black")
        colored_function = getattr(colored, color, lambda text: text)
        colored_output = colored_function(output)
        puts(colored_output)

logger = VirtstrapLogger()

VERBOSITY_LEVELS = {
    0: None,
    1: logging.WARNING,
    2: logging.INFO,
    3: logging.DEBUG,
}

def setup_logger(verbosity, no_colored_output=False, log_file=None):
    """Sets up the logger for the program. DO NOT USE DIRECTLY IN COMMANDS"""
    verbosity_level = VERBOSITY_LEVELS.get(verbosity, logging.INFO)
    if log_file:
        file_handler = FileLogHandler(log_file)
        # The file should log all things to be used for error reporting
        file_handler.set_level(logging.DEBUG)
        logger.add_handler(file_handler)
    if not verbosity_level:
        return
    console_handler = ConsoleLogHandler()
    if CLINT_AVAILABLE:
        console_handler = ColoredConsoleLogHandler()
    console_handler.set_level(verbosity_level)
    logger.add_handler(console_handler)
