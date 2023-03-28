# coding: utf-8
from __future__ import unicode_literals
import logging
import sys


class DebugOrInfo(logging.Filter):
    """Custom log filter that only matches DEBUG or INFO levels."""
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)


def get_logger():
    """Returns centralized logger."""
    logger = logging.getLogger('InQL')
    set_log_level(logger, 'INFO')

    return logger

def set_log_level(log, level):
    """Sets log level and generates handlers to pass DEBUG (if enabled) and INFO to stdout and WARN / ERR to stderr."""
    log.setLevel(level)

    formatter = logging.Formatter('[%(filename)s:%(lineno)d %(funcName)s()]    %(message)s')

    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setFormatter(formatter)
    handler_stdout.setLevel(logging.DEBUG)
    handler_stdout.addFilter(DebugOrInfo())

    handler_stderr = logging.StreamHandler(sys.stderr)
    handler_stderr.setFormatter(formatter)
    handler_stderr.setLevel(logging.WARNING)

    # Jython / Python 2.7 do not have log.handlers.clear(), but we can remove handlers like this:
    del log.handlers[:]

    log.addHandler(handler_stdout)
    log.addHandler(handler_stderr)
    
# Centralized log handler that gets used across InQL
log = get_logger()
set_log_level(log, 'WARNING')