"""
Breath color's, logo and other fun stuff!
"""

import subprocess

class Bling:
    """
    Collection of ANSII
    escape characters 
    and color codes.
    """
    CYAN = '\033[96m'
    ERROR = '\033[91m'
    WARNING = '\033[93m'
    FATAL = '\u001b[31m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def logo():
    """
    Outputs Breath logo
    """
    subprocess.run(['toilet', '-f', 'mono12', '-F', 'crop', 'Breath'])
    subprocess.run(['toilet', '-f', 'term', '-F', 'border', 'Made by MilkyDeveloper'])


def warning(message):
    """
    Print Breath warning(orange, bold).
    """
    return print(Bling.WARNING + Bling.BOLD + message + Bling.ENDC)

def error(message):
    """
    Print Breath error(orange, bold).
    """
    return print(Bling.ERROR + Bling.BOLD + message + Bling.ENDC)


def fatal(message):
    """
    Print Breath fatal error(red, bold).
    """
    return print(Bling.FATAL + Bling.BOLD + message + Bling.ENDC)


def cyan(message):
    """
    Print Breath cyan colored message(cyan, bold).
    """
    return print(Bling.CYAN + Bling.BOLD + message + Bling.ENDC)



def logo():
    """
    Prints Breath logo.
    Note: Toilet dependency is no longer required,
    although this does mean this is how we now have
    to handle the logo.
    Note: Wacky indentation prevents python from double-tabbing,
    the breath logo, as this is treated as a multiline string.
    """
    cyan('''
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
