#-*- encoding: utf-8 -*-

"""
Python Breath adaptation
"""

__title__ = 'breath'
__author__ = 'MilkyDeveloper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present MilkyDeveloper'
__version__ = '4.1.1-port/python'

import logging

from .errors import *

logging.getLogger(__name__).addHandler(logging.NullHandler())
