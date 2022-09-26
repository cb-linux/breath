# This script will later become the gui. For now, it's a simple wrapper for the build script.
import argparse
import sys

import build
import user_input
from functions import *


# parse arguments from the cli. Only for testing/advanced use. All other parameters are handled by user_input.py
def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--local-path', dest="local_path",
                        help="Use local files, instead of downloading from the internet (not recommended). Required "
                             "files: bzImage, modules.tar.xz, folder with firmware(named 'firmware'), Rootfs: "
                             "ubuntu-rootfs.tar.xz or arch-rootfs.tar.gz or fedora-rootfs.raw.xz or pre-debootstrapped "
                             "folder(named 'debian')")
    parser.add_argument("--dev", action="store_true", dest="dev_build", default=False,
                        help="Use latest dev build. May be unstable.")
    parser.add_argument("--alt", action="store_true", dest="alt", default=False,
                        help="Use alt kernel. Only for older devices.")
    parser.add_argument("--exp", action="store_true", dest="exp", default=False,
                        help="Use experimental 5.15 kernel.")
    parser.add_argument("--mainline", action="store_true", dest="mainline", default=False,
                        help="Use mainline linux kernel instead of modified chromeos kernel.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Print more output")
    return parser.parse_args()


if __name__ == '__main__':
    # Check python version
    if sys.version_info < (3, 10):  # python 3.10 or higher is required
        if path_exists("/usr/bin/apt"):
            if input(
                    "\033[92m" + "Python 3.10 or higher is required. Attempt to install?" + "\033[0m").lower() == "y" or "":
                print("Switching to unstable channel")
                # switch to unstable channel
                with open("/etc/apt/sources.list", "r") as file:
                    sources = file.readlines()
                sources[1] = sources[1].replace("bullseye", "unstable")
                with open("/etc/apt/sources.list", "w") as file:
                    file.writelines(sources)

                # update and install python
                print("Installing python 3.10")
                bash("apt update -y")
                bash("apt install -y python3")

            else:
                print("Please run the script with python 3.10 or higher")
                exit(1)
        else:
            print("Please run the script with python 3.10 or higher")
            exit(1)

    args = process_args()
    user_input = user_input.user_input()
    build = build.start_build(user_input, args)
