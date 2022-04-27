"""
Breath installation process
"""

from .functions import *
from .errors import *
import os


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
            run_root_cmd('sudo mkdir /mnt/breath')
            return '/mnt/breath'

        else:
            run_root_cmd('sudo mkdir /mnt')
            return '/mnt'

        
    @staticmethod
    def bootstrap_files(local_kernel, distro, mnt, original_dir):
        # This doesn't have to do with bootstrapping, but helps later
        # Exit if there are files in /mnt
        if os.listdir(mnt) != []:
            run_root_cmd(f'sudo rm -rf {mnt}/lost+found')
            raise DirectoryNotEmpty(f"There are files in {mnt}! Please clear this directory of any valuable information!")

        else:
            # Make the build directory and CD into it
            linux_build_dir = os.path.expanduser('~/linux-build')
            run_cmd(f'mkdir -p {linux_build_dir}')
            change_dir(linux_build_dir)

            # Copy or download kernel bzImage depending on local_kernel flag value.
            if local_kernel == True:
                try:
                    status('Copying kernel files from breath/kernel')
                    run_cmd(f'cp -v {original_dir}/kernel/bzImage .')
                    run_cmd(f'cp -v {original_dir}/kernel/modules.tar.xz .')
                    run_cmd(f'cp -v {original_dir}/kernel/kernel.flags .')
                    info('Copied kernel files')
                 
                except:
                   raise FileNotFound('Could not find a local kernel bzImage!') 

            else:
                # Download the kernel bzImage and the kernel modules with wget.
                status('Downloading kernel files from cb-linux/breath')
                run_cmd('wget https://github.com/cb-linux/breath/releases/latest/download/bzImage -O bzImage -q --show-progress')
                run_cmd('wget https://github.com/cb-linux/breath/releases/latest/download/modules.tar.xz -O modules.tar.xz -q --show-progress')
                run_cmd('wget https://raw.githubusercontent.com/cb-linux/kernel/main/kernel.flags -O kernel.flags -q --show-progress')
                info('Downloaded kernel files')

        # Download the root file system based on the distribution
        status(distro)




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




        
