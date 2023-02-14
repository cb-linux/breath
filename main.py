#!/usr/bin/env python3
# This script will later become the gui. For now, it's a simple wrapper for the build script.

import sys
import os
import argparse
import atexit

from functions import *


# parse arguments from the cli. Only for testing/advanced use. All other parameters are handled by cli_input.py
def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--local-path', dest="local_path",
                        help="Prefer local files instead of downloading from the internet(not recommended).")
    parser.add_argument('-d', '--device', dest="device_override",
                        help="Specify device to direct write. Skips the device selection question.")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                        help="Print more output")
    parser.add_argument("--no-shrink", action="store_true", dest="no_shrink", default=False,
                        help="Do not shrink image")
    parser.add_argument("--image-size", "-i", dest="image_size", type=int, nargs=1, default=[10],
                        help="Override image size(default: 10GB)")
    parser.add_argument("--dev", action="store_true", dest="dev_build", default=False,
                        help="Use latest dev build. May be unstable.")
    return parser.parse_args()


def exit_handler():
    if not script_finished:
        print_error("Script exited unexpectedly")
        print_question('Run "./main.py -v" to restart with more verbose output\n'
                       'Run "./main.py --help" for more options')


if __name__ == "__main__":
    args = process_args()
    if args.dev_build:
        print_error("Dev builds are not supported currently")
        exit(1)
    atexit.register(exit_handler)
    script_finished = False

    # Restart script as root
    if os.geteuid() != 0:
        sudo_args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)

    # check script dependencies are already installed with which
    try:
        bash("which pv xz parted cgpt futility")
        print_status("Dependencies already installed, skipping")
    except subprocess.CalledProcessError:
        print_status("Installing dependencies")
        with open("/etc/os-release", "r") as os:
            distro = os.read()
        if distro.__contains__("Arch Linux"):
            bash("pacman -Sy")  # sync repos
            bash("pacman -S --noconfirm --needed debootstrap")
            # Download prepackaged cgpt + vboot from arch-repo releases as its not available in the official repos
            # Makepkg is too much of a hassle to use here as it requires a non-root user
            urlretrieve("https://github.com/eupnea-linux/arch-repo/releases/latest/download/cgpt-vboot"
                        "-utils.pkg.tar.gz", filename="/tmp/cgpt-vboot-utils.pkg.tar.gz")
            # Install downloaded package
            bash("pacman --noconfirm -U /tmp/cgpt-vboot-utils.pkg.tar.gz")
            # Install other dependencies
            bash("pacman --noconfirm -S pv xz parted")
        elif distro.__contains__("Void"):
            bash("xbps-install -y --sync")
            bash("xbps-install -y pv xz parted cgpt vboot-utils")
        elif distro.__contains__("Ubuntu") or distro.__contains__("Debian"):
            bash("apt-get update -y")  # sync repos
            bash("apt-get install -y pv xz-utils parted cgpt vboot-kernel-utils")
        elif distro.__contains__("SUSE"):
            bash("zypper --non-interactive refresh")  # sync repos
            bash("zypper --non-interactive install vboot parted pv xz")  # cgpt is included in vboot-utils on fedora
        elif distro.__contains__("Fedora"):
            bash("dnf update -y")  # sync repos
            bash("dnf install -y vboot-utils parted pv xz")  # cgpt is included in vboot-utils on fedora
        else:
            print_warning("Debootstrap not found, please install it using your distros package manager or select "
                          "another distro instead of debian")
            exit(1)

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
            if user_answer in ["y", ""]:
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
            else:
                print_error("Please run the script with python 3.10 or higher")
        else:
            print_error("Please run the script with python 3.10 or higher")
        script_finished = True
        exit(0)
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
    if args.image_size[0] != 10:
        print_warning(f"Image size overridden to {args.image_size[0]}GB")

    # override device if specified
    if args.device_override is not None:
        user_input = cli_input.get_user_input(skip_device=True)  # get user input
        user_input["device"] = args.device_override  # override device
    else:
        user_input = cli_input.get_user_input()  # get normal user input

    # Check if there is enough space in /tmp
    avail_space = int(bash("df -h --output=avail /tmp").split(" ")[1][:-1])  # get available space in /tmp as int in GB

    if user_input["device"] == "image" and avail_space < 11:
        print_error("Not enough space in /tmp to build image. At least 5GB is required")
        user_answer = input("\033[92m" + "Attempt to increase size of /tmp? (Y/n)\n" + "\033[0m").lower()
        if user_answer in ["y", ""]:
            print_status("Increasing size of /tmp")
            bash("mount -o remount,size=5G /tmp")
            print_status("Size of /tmp increased")
        else:
            print_error("Please free up space in /tmp")
            exit(1)

    build.start_build(verbose=args.verbose, local_path=args.local_path, dev_release=args.dev_build,
                      build_options=user_input, no_shrink=args.no_shrink, img_size=args.image_size[0])
    script_finished = True
