#-*- encoding: utf-8 -*-

"""
Python Breath adaptation
"""

__title__ = 'breath'
__summary__ = 'A way to natively run Linux on modern Chromebooks without replacing firmware.'
__author__ = 'MilkyDeveloper'
__license__ = 'MIT'
__copyright__ = 'Copyright 2021-present MilkyDeveloper'
__version__ = '4.1.1-port/python'

import subprocess
import traceback
import argparse
import sys

# The default configuration options for Breath.
# Used for comparison between user options and defaults
# to determine if user interaction is necessary.
# NOTE: Changing these values changes Breath defaults!
defaults = {
    'install_type': 'usb', 
    'distro': 'ubuntu', 
    'desktop': 'cli', 
    'hostname': 'chromebook', 
    'username': 'breath', 
    'password': 'breath_passwd',
    'keymap': False,
    'crostini': False,
    'local_kernel': False,
    'force_defaults': False,
    'cleanup': False,
    'verbose': False,
    'view_defaults': False,
    'version': False
}


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


def define_and_parse_args():
    # TODO: Fix command-line formatting(Several wacky things like indentation between long and short args).
    # TODO: Add nargs for short help.
    """
    Define command-line arguments.
    """
    fmt = lambda prog: CustomHelpFormatter(prog)

    parser = argparse.ArgumentParser(
        prog=__title__,
        usage='&(prog)s [options...]',
        description=__summary__,
        formatter_class=fmt
    )

    parser.add_argument('-t', '--install_type', default=defaults['install_type'], choices=['usb', 'iso'], help='choose installation type (default: %(default)s)')
    parser.add_argument('-d', '--distro', default=defaults['distro'], choices=['arch', 'debian', 'fedora', 'ubuntu'], help='choose distro (default: %(default)s)')
    parser.add_argument('-de', '--desktop', default=defaults['desktop'], choices=['cli', 'gnome', 'kde', 'minimal', 'deepin', 'budgie', 'fce', 'lxqt', 'mate', 'openbox'], help='choose desktop environment (default: %(default)s)')
    parser.add_argument('-hn', '--hostname', default=defaults['hostname'], help='set hostname (default: %(default)s)')
    parser.add_argument('-u', '--username', default=defaults['username'], help='set username (default: %(default)s)')
    parser.add_argument('-p', '--password', default=defaults['password'], help='set password (default: %(default)s)')
    parser.add_argument('-k', '--keymap', default=defaults['keymap'], help='map keys to chromebook actions (default: %(default)s)', action='store_true')
    parser.add_argument('-c', '--crostini', default=defaults['crostini'], help='installer using a chrome-based system (default: %(default)s)', action='store_true')
    parser.add_argument('-lk', '--local_kernel', default=defaults['local_kernel'], help='use a local build of the kernel bzImage (default: %(default)s)', action='store_true')
    parser.add_argument('-f', '--force_defaults', default=defaults['force_defaults'], help='install with default configuration (see defaults)', action='store_true')
    parser.add_argument('-vd', '--view_defaults', default=defaults['view_defaults'], help='view default configuration options', action='store_true')
    parser.add_argument('-v', '--version', default=defaults['version'], help='output version information and exit', action='store_true')

    # Parse args
    args = parser.parse_args()

    # Add argparse options to dict(user_input)
    user_input = (vars(args))

    if args.view_defaults:
        info(defaults)
        sys.exit()

    elif args.version:
        info(f'{__title__} v{__version__}')
        sys.exit()

    else:
        print(parser.print_help())
        sys.exit()

    return user_input


def run_as_a_module():
    """
	Since we're running this as a 'python -m archinstall' module
	or a compiled version of the project, this function 
    and the file '__main__.py' acts as a entry point.
	"""

    # Argparse command-line parsers
    # NOTE: Runs only if ran as a module
    options = define_and_parse_args()

    try:
        # Exit if running as root.
        if os.geteuid() == 0:
            sys.tracebacklimit = 0 # set as options is not yet defined
            raise DontRunAsRoot('Please do not run Breath as root!')

        # Run core installer here and pass options

    except Exception:
        """
        CPrint any exception not defined in Breath if caught.
        NOTE: Verbosity levels ignored since an exception
        thrown by python is usually a bug.
        """
        sys.exit()
