"""
Breath installation process
"""

from .functions import *
from .errors import *

system_passwd = None # Necessary for run_root_cmd()


class BreathInstaller:
    """
    Breath installer abstraction.
    NOTE: The below functions do not require a class,
    but as of now this structure makes more sense
    when looing at the project topology currently.
    """


    @staticmethod
    def check_crostini(crostini):
        # crostini -> True
        if crostini == True:
            run_root_cmd('sudo mkdir /mnt/breath', system_passwd)
        
        # crostini -> False
        elif crostini == False:
            pass


    @staticmethod
    def bootstrap_files(local_kernel, distro):
        pass


    @staticmethod
    def configure_install_type(install_type):
        # install_type -> usb
        if install_type == 'iso':
            status(f'Building ISO at {os.pwd()}/breath.img')
            run_cmd('sleep 10')
            run_cmd('fallocate -l 12G breath.img')
            

        # install_type -> iso
        elif install_type == 'usb':
            pass




        
