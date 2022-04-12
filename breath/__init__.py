#-*- encoding: utf-8 -*-

"""
Python Breath adaptation
"""

__title__ = 'breath'
__summary__ = 'A way to natively run Linux on modern Chromebooks without replacing firmware'
__author__ = 'MilkyDeveloper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present MilkyDeveloper'
__version__ = '4.1.1-port/python'

import argparse
import sys

#from .errors import *
from .system import *
from .input import *
from .settings import *

options = dict() # This dict will hold all the install options for the breath installer to use

class CustomHelpFormatter(argparse.HelpFormatter):
    """
    Custom argparse help formatter. Currently this allows for the following:
    - Disables metavar for short args. Example without(-t {usb, iso} --type {usb, iso}) | Example with(-t --type {usb, iso})
    - Allows for extending the default column size for help variables.
    """
    def __init__(self, prog):
        super().__init__(prog, max_help_position=100, width=180)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string

fmt = lambda prog: CustomHelpFormatter(prog)

parser = argparse.ArgumentParser(
    prog=__title__,
    usage='%(prog)s [options...]',
    description=__summary__,
    formatter_class=fmt
)

def define_arguments():
    """
    Define command-line arguments.
    """
    parser.add_argument('-t', '--installtype', default='usb', choices=['usb', 'iso'], help='choose installation type (default: %(default)s)')
    parser.add_argument('-k', '--keymap', help='map keys to chromebook actions', action='store_true')
    parser.add_argument('-d', '--distro', default='ubuntu', choices=['arch', 'debian', 'fedora', 'ubuntu'], help='choose distro (default: %(default)s)')
    parser.add_argument('-de', '--desktop', default='cli', choices=['cli', 'gnome', 'kde', 'minimal', 'deepin', 'budgie', 'fce', 'lxqt', 'mate', 'openbox'], help='choose desktop environment (default: %(default)s)')
    parser.add_argument('-hn', '--hostname', default='chromebook', help='set hostname (default: %(default)s)')
    parser.add_argument('-u', '--username', default='breath_user', help='set username (default: %(default)s)')
    parser.add_argument('-p', '--password', default='breath_passwd', help='set password (default: %(default)s)')
    parser.add_argument('-sp', '--systempasswd', help='input system password for root access, needed to run breath!')
    parser.add_argument('-c', '--crostini', help='add this flag if installing on a chrome-based system!', action='store_true')
    parser.add_argument('-f', '--forcedefaults', help='forces breath to install without any configuration (see default in [options])', action='store_true')
    parser.add_argument('-vv', '--verbose', help='set installer output to verbose', action='store_true')
    parser.add_argument('-v', '--version', help='output version information and exit', action='store_true')

def parse_arguments():
    """
    Parse arguments. If none inputted, use defaults.
    """
    args = parser.parse_args()

    # Update argparse.Namespace() contents to dict(installation_options)
    options.update(vars(args))

    if args.version:
        print(f'{__title__} v{__version__}')
        sys.exit()

define_arguments()
parse_arguments()

def run_as_a_module():
    """
	Since we're running this as a 'python -m archinstall' module
	or a nuitka3 compiled version of the project, this function 
    and the file '__main__.py' acts as a entry point.
	"""

    # Set verbosity level of traceback
    set_verbosity_level(options['verbose'])

    # Check what type of operating system is being used, if it 
    # is Windows or Darwin, exit. This also sets up any os abstraction
    # for the installer later on.
    system, distro = system_details()

    # If the system and/or distribution is supported, but the user
    # did not specify any flags, assume the user needs to set everything.
    # This brings up installation inputs, after which installation proceeds with set flags. 
    # NOTE: If --forcedefaults is used, then use default args.
    if options['forcedefaults'] == False:
        new_options = input_options(options)

    else:
        pass
    





