#-*- encoding: utf-8 -*-

"""
Python Breath adaptation
"""

__title__ = 'breath'
__author__ = 'MilkyDeveloper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present MilkyDeveloper'
__version__ = '4.1.1-port/python'

from argparse import ArgumentParser
import sys

from .system import *


def define_arguments():
    """
    Define command-line arguments.
    """
    parser = ArgumentParser(description=logo())
    parser.add_argument('-v', '--version', required=False, help='output version information and exit', action='store_true')


def parse_arguments():
    """
    Parse arguments. If none inputted, default to '--help'.
    """
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])


define_arguments()
parse_arguments()

def run_as_a_module():
    """
	Since we're running this as a 'python -m archinstall' module
	or a nuitka3 compiled version of the project, this function 
    and the file '__main__.py' acts as a entry point.
	"""
    pass
    

