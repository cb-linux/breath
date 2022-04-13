"""
Breath user interactions
"""

from .bling import *

def determine_configuration(defaults, user_input):
    """
    Determine if the user has set any flags.
    If the flags are all default and '--forcedefaults'
    is not set, guide user through a cli installer.
    Returns dict(new_options).
    """

    # Keep user_input the same if forcedefaults is set
    if user_input['force_defaults'] == True:
        return user_input

    # Guide user through a cli installer if defaults match user_input
    if user_input == defaults:

        # Ask user for installation type. Possible choices(usb, iso).
        install_type = ask_for_install_type(user_input['-install_type'])

        return 
        

    # If the user configured installation via argparse, skip cli config
    else:
        return user_input


def get_password():
    """
    Password prompt with password validity check.
    """
    pass


def ask_for_install_type(install_type):
    """
    Ask user for install_type.
    Options: ['usb', 'iso']
    """
    pass


def ask_for_distro(distro):
   """
   Ask user for distro to install.
   Options: ['arch', 'debian', 'fedora', 'ubuntu']
   """
   pass


def ask_for_desktop(desktop):
    """
    Ask user for desktop environment.
    Options; ['cli', 'gnome', 'kde', 'minimal', 'deepin', 'budgie', 'fce', 'lxqt', 'mate', 'openbox']
    """
    pass


def ask_for_hostname(hostname):
    """
    Ask user for breath install hostname.
    Must be 2 characters minimum; 63 characters max.
    Can contain digits, lower case letters, hyphens, and dots.
    """
    pass


def ask_for_username(username):
    """
    Ask user for breath root username.
    Must begin with a lowercase letter or underscore,
    followed by lower case letters, digits, underscores,
    or dashes.
    """
    pass


def ask_for_system_password(system_password):
    """
    Ask user for root(host system) password.
    Needed to run certain commands and installation steps.
    """
    pass


def ask_to_set_keymap(keymap):
    """
    Ask user to map keys to Chromebook standard.
    """
    pass


def ask_if_running_crostini(crostini):
    """
    Ask user if host system is running crostini(chrome-based).
    """
    pass


def ask_verbosity_level(verbose):
    """
    Ask user if the installer should run with verbose flag set.
    """
    pass
