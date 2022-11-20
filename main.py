#!/usr/bin/env python3
# This script will later become the gui. For now, it's a simple wrapper for the build script.

import sys
import os
import argparse

from functions import *


# parse arguments from the cli. Only for testing/advanced use. All other parameters are handled by cli_input.py
def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local-path', dest="local_path",
                        help="Prefer local files instead of downloading from the internet(not recommended).")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Print more output")
    parser.add_argument("--no-shrink", action="store_true", dest="no_shrink", default=False,
                        help="Do not shrink image")
    parser.add_argument("--image-size", "-i", dest="image_size", type=int, nargs=1, default=[10],
                        help="Override image size(default: 10GB)")
    parser.add_argument("--dev", action="store_true", dest="dev_build", default=False,
                        help="Use latest dev build. May be unstable.")
    parser.add_argument("--alt", action="store_true", dest="alt", default=False,
                        help="Use alt kernel. Only for older devices.")
    parser.add_argument("--exp", action="store_true", dest="exp", default=False,
                        help="Use experimental 5.15 kernel.")
    parser.add_argument("--mainline", action="store_true", dest="mainline", default=False,
                        help="Use mainline linux kernel instead of modified chromeos kernel.")
    return parser.parse_args()


if __name__ == "__main__":
    args = process_args()

    # Restart script as root
    if not os.geteuid() == 0:
        sudo_args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)

    # install dependencies
    install_kernel_packages()

    # Check python version
    if sys.version_info < (3, 10):  # python 3.10 or higher is required
        # Check if running under crostini and ask user to update python
        # Do not give this option on regular systems, as it may break the system
        try:
            with open("/sys/devices/virtual/dmi/id/product_name", "r") as file:
                product_name = file.read().strip()
        except FileNotFoundError:
            product_name = ""
        if product_name == "crosvm" and path_exists("/usr/bin/apt"):
            user_answer = input("\033[92m" + "Python 3.10 or higher is required. Attempt to install? (Y/n)\n" +
                                "\033[0m").lower()
            if user_answer == "y" or user_answer == "":
                print_status("Switching to unstable channel")
                # switch to unstable channel
                with open("/etc/apt/sources.list", "r") as file:
                    original_sources = file.readlines()
                sources = original_sources
                sources[1] = sources[1].replace("bullseye", "unstable")
                with open("/etc/apt/sources.list", "w") as file:
                    file.writelines(sources)

                # update and install python
                print_status("Installing python 3.10")
                bash("apt-get update -y")
                bash("apt-get install -y python3")
                print_status("Python 3.10 installed")

                # revert to stable channel
                with open("/etc/apt/sources.list", "w") as file:
                    file.writelines(original_sources)

                bash("apt-get update -y")  # update cache back to stable channel

                print_header('Please restart the script with: "./main.py"')
                exit(1)
            else:
                print_error("Please run the script with python 3.10 or higher")
                exit(1)
        else:
            print_error("Please run the script with python 3.10 or higher")
            exit(1)

    # import other scripts after python version check is successful
    import build
    import cli_input

    # Check if running under crostini
    try:
        with open("/sys/devices/virtual/dmi/id/product_name", "r") as file:
            product_name = file.read().strip()
    except FileNotFoundError:
        product_name = ""  # WSL has no dmi data
    if product_name == "crosvm" and not path_exists("/tmp/.crostini-fixed"):
        print_warning("Crostini detected. Preparing Crostini")
        # TODO: Translate to python
        try:
            bash("bash configs/crostini/setup-crostini.sh")
        except subprocess.CalledProcessError:
            print_error("Failed to prepare Crostini")
            print_error("Please run the Crostini specific instructions before running this script")
            print("https://eupnea-linux.github.io/main.html#/extra-pages/crostini")
            exit(1)
        open("/tmp/.crostini-fixed", "a").close()

    # parse arguments
    if args.dev_build:
        print_warning("Using dev release")
    if args.local_path:
        print_warning("Using local files")
    if args.verbose:
        print_warning("Verbosity increased")
    if args.no_shrink:
        print_warning("Image will not be shrunk")
    if not args.image_size[0] == 10:
        print_warning(f"Image size overridden to {args.image_size[0]}GB")

    # get user input
    user_input = cli_input.get_user_input()

    build.start_build(verbose=args.verbose, local_path=args.local_path, kernel_type=user_input["kernel_type"],
                      dev_release=args.dev_build, build_options=user_input, no_shrink=args.no_shrink,
                      img_size=args.image_size[0])
