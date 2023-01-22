# coding: utf-8
from __future__ import unicode_literals
from builtins import object
import logging


class Logger(object):
    logger = None

    def __init__(self):
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.WARNING)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def err(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    @property
    def is_debug(self):
        return self.logger.level <= logging.DEBUG


log = Logger()
