"""
Breath installation process
"""

from .functions import *
from .errors import *

class BreathInstaller:
    def __init__(self, options, defaults, system_passwd=None):
        self.system_passwd = system_passwd
        self.install_type = options['install_type']
        self.distro = options['distro']
        self.desktop = options['desktop']
        self.hostname = options['hostname']
        self.username = options['username']
        self.password = options['password']
        self.keymap = options['keymap']
        self.crostini = options['crostini']


        
