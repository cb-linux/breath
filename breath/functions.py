"""
Breath functions
"""
from cprint import *
import subprocess
import pwinput
import sys


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
    subprocess.run(command.split())


def run_root_cmd(command, system_passwd):
    """
    Run a command as root.
    """
    proc = subprocess.Popen(command.split(), stdin=subprocess.PIPE, stdout=sys.stdout, stderr=subprocess.PIPE)
    proc.communicate(input=b'{system_password}\n')


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

