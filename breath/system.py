"""
Breath host system abstraction
"""

from shutil import which
import platform
import distro
import os

from .interactions import *
from .functions import *
from .errors import *


class BreathSystem:
    """
    The host system abstraction.
    """
    def __init__(self, system_passwd=None):
        self.system_passwd = system_passwd
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
        elif system_passwd is None:
            pass # Disabled as this is properly working yet.
            #self.system_passwd = get_password()


    def update_packages(self):
        """
        Updates host system packages.
        """
        status('Updating system packages...')

        if self.distro == 'debian' or self.distro == 'ubuntu':
            run_root_cmd('sudo apt update -y && sudo apt upgrade -y', self.system_passwd)

        elif self.distro == 'arch':
            run_root_cmd('sudo pacman -Syyu', self.system_passwd)

        elif self.distro == 'fedora':
            run_root_cmd('sudo dnf upgrade --assumeyes', self.system_passwd)

    
    def install_dependencies(self, packages):
        """
        Install host system dependencies for Breath.
        """
        status('Installing breath dependencies...')

        # NOTE: Packages are named differently across distributions, namely Arch.
        # The below if statements handle all of that for us.
        # TODO: Clean up(There has got to be a better way to format lists)
        if self.distro == 'debian' or self.distro == 'ubuntu':
            packages = ' '.join(packages)
            run_root_cmd(f'sudo apt install -y {packages}', self.system_passwd)

        elif self.distro == 'arch':
            for i in range(len(packages)):
                if packages[i] == 'vboot-kernel-utils':
                    packages[i] = 'vboot-utils'

                elif packages[i] == 'cgpt':
                    del packages[i]

                elif packages[i] == 'cloud-guest-utils':
                    packages[i] = 'growpartfs'

            packages = ' '.join(packages)
            run_root_cmd(f'yay -S {packages} --noconfirm', self.system_passwd)

        elif self.distro == 'fedora':
            packages = ' '.join(packages)
            run_root_cmd(f'sudo dnf install {packages} --assumeyes', self.system_passwd)
