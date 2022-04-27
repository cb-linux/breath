"""
Breath functions
"""
from cprint import *
import subprocess
import pwinput
import sys
import os

def get_password():
    """
    Get root host system password.
    """
    # TODO: Add password validation
    return pwinput.pwinput(prompt=f'Root password for {os.getlogin()}: ', mask='*')


def run_cmd(command):
    """
    Run a command.
    """
    try:
        subprocess.check_output(command.split(), stderr=subprocess.STDOUT)

    except subprocess.CalledProcessError:
        raise BreathException


def run_root_cmd(command, system_passwd=None):
    """
    Run a command as root.
    """
    proc = subprocess.Popen(command.split(), stdin=subprocess.PIPE, stdout=sys.stdout, stderr=subprocess.PIPE)
    proc.communicate(input=b'{system_password}\n')


def export(var_name, var_contents):
    """
    Export an environment variable.
    """
    os.environ[var_name] = var_contents


def view_export(var_name):
    """
    View the contents of an environment variable and return'
    """
    return os.getenv(var_name)


def change_dir(directory):
    """
    Change breath current directory.
    """
    os.chdir(directory)


def status(message):
    """
    Print Breath ok(blue, bold).
    """
    return cprint.ok(message, bold=True)


def info(message):
    """
    Print Breath info(green, bold).
    """
    return cprint.info(message, bold=True)


def warning(message):
    """
    Print Breath warning(yellow, bold).
    """
    return cprint.warn(message, bold=True)


def error(message):
    """
    Print Breath error(orange, bold, program interrupt[handled by installer to suppress cprint extra output]).
    """
    return cprint.err(message, bold=True)


def fatal(message):
    """
    Print Breath fatal error(red, bold, program interrupt).
    """
    return cprint.fatal(message, bold=True, interrupt=True)


def cli_format():
    """
    A nice way to format the cli menu and logo.
    """
    run_cmd('clear')
    logo()


def logo():
    """
    Prints Breath logo.
    Note: Toilet dependency is no longer required,
    although this does mean this is how we now have
    to handle the logo.
    Note: Wacky indentation prevents python from double-tabbing,
    the breath logo, as this is treated as a multiline string.
    """
    print('''
▄▄▄▄▄▄                                            ▄▄      
██▀▀▀▀██                                  ██      ██      
██    ██   ██▄████   ▄████▄    ▄█████▄  ███████   ██▄████▄
███████    ██▀      ██▄▄▄▄██   ▀ ▄▄▄██    ██      ██▀   ██
██    ██   ██       ██▀▀▀▀▀▀  ▄██▀▀▀██    ██      ██    ██
██▄▄▄▄██   ██       ▀██▄▄▄▄█  ██▄▄▄███    ██▄▄▄   ██    ██
▀▀▀▀▀▀▀    ▀▀         ▀▀▀▀▀    ▀▀▀▀ ▀▀     ▀▀▀▀   ▀▀    ▀▀
┌──────────────────────┐                                  
│Made by MilkyDeveloper│          
└──────────────────────┘
    ''')

