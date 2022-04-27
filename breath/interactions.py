"""
Breath user interactions
"""

from .output import *
from blessed import Terminal
from getpass import getpass
import inquirer
import re
import os


class BreathInquirerTheme(inquirer.themes.Theme):
    """
    Breath theming for inquirer cli menu.
    """
    def __init__(self):
        super().__init__()
        self.term = Terminal()
        self.Question.mark_color = self.term.yellow
        self.Question.brackets_color = self.term.bright_green
        self.Question.default_color = self.term.yellow
        self.List.selection_color = self.term.bright_green
        self.List.selection_cursor = "❯"
        self.List.unselected_color = self.term.normal


def BreathInquirer(defaults, user_input):
    """
    Determine if the user has set any flags.
    If the flags are all default and '--forcedefaults'
    is not set, guide user through a cli installer.
    Returns dict(new_options).
    """
    # TODO: Turn this functions into a class, which will help return back
    # to the inquirer at any point in the installation if something goes wrong,
    # or for another reason.

    # Keep user_input the same if forcedefaults is set
    if user_input['force_defaults'] == True:
        return user_input

    # Guide user through a cli installer if defaults match user_input
    elif user_input == defaults:
        questions = [
            inquirer.List('install_type',
                message='Installation type',
                choices=['usb', 'iso'],
                default=defaults['install_type'],
            ),
            inquirer.List('distro',
                message='Distro of choice',
                choices=['arch', 'debian', 'fedora', 'ubuntu'],
                default=defaults['distro'],
            ),
            inquirer.List('desktop',
                message='Desktop environment',
                choices=['cli', 'gnome', 'kde', 'minimal', 'deepin', 'budgie', 'xfce', 'lxqt', 'mate', 'openbox'],
                default=defaults['desktop'],
            ),
            inquirer.Text('hostname',
                message='Breath Hostname',
                validate=lambda _, x: re.match('(?:^|\\s)[a-z]+(?:\\s|$)', x),
                default=defaults['hostname'],
            ),
            inquirer.Text('username',
                message='Breath Username',
                validate=lambda _, x: re.match('(?:^|\\s)[a-z]+(?:\\s|$)', x),
                default=defaults['username'],
            ),
            inquirer.Password('password',
                message='Breath Password',
                validate=lambda _, x: re.match('^\S+$', x),
            ),
            inquirer.Confirm('keymap',
                message='Map keys to chromebook actions?',
                default=defaults['keymap'],
            ),
            inquirer.Confirm('crostini',
                message='Is this a crostini(chrome) system?',
                default=defaults['crostini'],
            ),
            inquirer.Confirm('verbose',
                message='Set verbose installation output?',
                default=defaults['verbose'],
            ),
        ]

        user_input = inquirer.prompt(questions, theme=BreathInquirerTheme())
        return user_input

    # If the user configured installation via argparse, skip cli config
    else:
        return user_input
