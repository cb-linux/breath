from shutil import which
import subprocess
import platform
import pwinput
import distro
import sys
import os

from .interactions import *
from .errors import *
from .output import *

from subprocess import Popen, PIPE

def get_password():
    """
    Get root host system password.
    """
    # TODO: Add password validation
    return pwinput.pwinput(prompt=f'Root password for {os.getlogin()}: ', mask='*')


def run_as_root(command, system_password):
    """
    Run a command as root.
    """
    # TODO: Fix stdin not reading password properly.
    proc = Popen(command, stdin=PIPE, stdout=PIPE)
    proc.communicate(system_password.encode())


class BreathSystem:
    """
    The host system abstraction.
    """
    def __init__(self, system_password=None):
        self.platform = platform.system()
        self.distro = distro.id()

        # Raise error if distro unsupported
        if self.distro not in ('arch', 'debian', 'fedora', 'ubuntu'):
            raise DistributionNotSupported(f'{distro} is not currently supported!')

        # Windows and Darwin unsupported
        elif self.platform in ('Windows', 'Darwin'):
            raise PlatformNotSupported(f'{platform} is not currently supported!')

        # Undetermined unsupported
        elif self.platform not in ('Windows', 'Darwin', 'Linux'):
            raise UndeterminedSystem(f'{platform} is an unsupported system!')

        # Yay aur helper needs to be installed on an arch-based host system
        elif self.distro == 'arch' and which('yay') is None:
            raise YayNotFound(f'Breath requires the yay aur helper to be installed!')

        # Ask user for root password for host system if system_passwd is None
        elif system_password is None:
            self.system_password = get_password()


    def update_packages(self):
        cyan('Updating system packages...')

        if self.distro == 'debian' or self.distro == 'ubuntu':
            run_as_root(['sudo', 'apt', 'update' '&&' 'upgrade'], self.system_password)

        elif self.distro == 'arch':
            run_as_root(['yay', '-Syyu'], self.system_password)

        elif self.distro == 'fedora':
            run_as_root(['sudo', 'dnf', 'upgrade'], self.system_password)


