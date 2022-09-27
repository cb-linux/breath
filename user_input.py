#!/usr/bin/env python3

from typing import Tuple
import json
from getpass import getpass
from functions import bash


def user_input() -> Tuple[str, str, str, str, str, str, str, str, bool, bool]:
    # set default values
    distro_version = 0
    distro_link = ""
    username = ""
    password = ""

    # Print welcome message
    print("\033[95m" + "Welcome to Eupnea" + "\033[0m")
    print("\033[95m" + "This script will create a bootable Eupnea USB Stick/SD-card" + "\033[0m")
    print("\033[95m" + "Please answer the following questions." "\033[0m")
    print("(If you dont know what to answer, just press enter and the recommended answer will be used)")
    print("\033[92m" + "Which Linux distro(flavor) would you like to use?" + "\033[0m")

    with open("distros.json", "r") as file:
        distros = json.load(file)

    while True:
        temp_distro_name = input("\033[94m" + "Available options: Ubuntu(default, recommended), Debian, Arch, Fedora\n"
                                 + "\033[0m")
        match temp_distro_name:
            case "Ubuntu" | "ubuntu" | "":
                distro_name = "ubuntu"
                while True:
                    print("\033[92m" + "Use latest Ubuntu version?" + "\033[0m")
                    distro_version = input("\033[94mPress enter for yes, or type in the version number(example: "
                                           "'21.10'):\n" + "\033[0m")
                    if distro_version == "":
                        # get highest version number
                        distro_version = max(distros["ubuntu"])
                        distro_link = distros["ubuntu"][distro_version]
                        print("Latest Ubuntu: " + distro_version + " selected")
                        break
                    else:
                        if distro_version in distros["ubuntu"]:
                            distro_link = distros["ubuntu"][distro_version]
                            print("Ubuntu: " + distro_version + " codename: " + distros["ubuntu"][distro_version] +
                                  " selected")
                            break
                        else:
                            print("\033[93m" + "Version not available, please choose another" + "\033[0m")
                            continue
                break
            case "Debian" | "debian":
                print("Debian stable selected")
                distro_name = "debian"
                # TODO: Add non stable debian versions
                break
            case "Arch" | "arch" | "arch btw":
                print("Arch selected")
                distro_name = "arch"
                distro_link = distros["arch"]
                break
            case "Fedora" | "fedora":
                distro_name = "fedora"
                while True:
                    print("\033[92m" + "Use latest Fedora version?" + "\033[94m")
                    temp_input = input("Press enter for yes, or type in the version number(example: '35').\033[0m\n")
                    if temp_input == "":
                        # remove rawhide, then get the highest version number
                        temp_fedora_dict = distros["fedora"]
                        temp_fedora_dict.pop("Rawhide")
                        distro_version = max(temp_fedora_dict)
                        distro_link = distros["fedora"][distro_version]
                        print("Using Fedora version: " + distro_version)
                        break
                    else:
                        try:
                            distro_version = temp_input
                            distro_link = distros["fedora"][distro_version]
                            print("Using Fedora version: " + distro_version)
                            break
                        except KeyError:
                            print("\033[93m" + "Fedora version not available, please choose another" + "\033[0m")
                            continue
                break
            case _:
                print("\033[93mCheck your spelling and try again" + "\033[0m")
                continue

    print("\033[92m" + "Which desktop environment(interface) would you like to use?" + "\033[0m")
    match distro_name:
        case "ubuntu":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), deepin, budgie, cli"
        case "debian":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), budgie, cli"
        case "arch":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), deepin, budgie, cli"
        case "fedora":
            available_de = "Gnome(default, recommended), KDE(recommended), MATE, Xfce(recommended for weak devices), " \
                           "LXQt(recommended for weak devices), deepin, cli"

    while True:
        de_name = input("\033[94m" + "Available options: " + available_de + "\033[0m" + "\n")
        match de_name:
            case "Gnome" | "gnome" | "":
                print("Gnome selected")
                de_name = "gnome"
                break
            case "KDE" | "kde":
                print("KDE selected")
                de_name = "kde"
                break
            case "MATE" | "mate":
                print("MATE selected")
                de_name = "mate"
                break
            case "xfce" | "Xfce":
                print("Xfce selected")
                de_name = "xfce"
                break
            case "lxqt" | "Lxqt":
                print("Lxqt selected")
                de_name = "lxqt"
                break
            case "deepin":
                if distro_name == "debian":
                    print("\033[93m" + "Deepin is not available for Debian, please choose another DE" + "\033[0m")
                else:
                    print("Deepin selected")
                    de_name = "deepin"
                    break
            case "budgie":
                if distro_name == "fedora":
                    print("\033[93m" + "Budgie is not available for Fedora, please choose another DE" + "\033[0m")
                else:
                    print("Budgie selected")
                    de_name = "budgie"
                    break
            case "cli" | "none":
                print("\033[93m" + "Warning: No desktop environment will be installed!")
                if input("\033[94mType 'yes' to continue or Press Enter to choose a desktop environment" +
                         "\033[0m\n") == "yes":
                    print("No desktop will be installed")
                    de_name = "cli"
                    break
            case _:
                print("\033[93m" + "Check your spelling and try again" + "\033[0m")

    # Ubuntu + gnome now has a first time setup, so skip this part for ubuntu with gnome
    if not (distro_name == "ubuntu" and de_name == "gnome"):
        print("\033[92m" + "Enter username to be used in Eupnea" + "\033[0m")
        while True:
            username = input("\033[94m" + "Username(default: 'localuser'): " + "\033[0m")
            for char in username:
                if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
                    print("\033[93m" + "Username contains invalid character: " + char + "\033[0m")
                    break
            if username == "":
                print("Using localuser as username")
                username = "localuser"
                break
            else:
                break

        print("\033[92m" + "Please set a secure password" + "\033[0m")
        while True:
            passwd_temp = getpass("\033[94m" + "Password: " + "\033[0m")
            if passwd_temp == "":
                print("\033[93m" + "Password cannot be empty" + "\033[0m")
                continue
            # TODO: Fix ) and ( crashing chpasswd
            elif passwd_temp.find(")") != -1:
                print("\033[93m" + "Password cannot contain: )" + "\033[0m")
                continue
            elif passwd_temp.find("(") != -1:
                print("\033[93m" + "Password cannot contain: (" + "\033[0m")
                continue
            else:
                passwd_temp_2 = getpass("\033[94m" + "Repeat password: " + "\033[0m")
                if passwd_temp == passwd_temp_2:
                    password = passwd_temp
                    print("Password set")
                    break
                else:
                    print("\033[93m" + "Passwords do not match, try again" + "\033[0m")
                    continue

    print("\033[92m" + "Enter hostname for the chromebook.(Hostname is something like a device name)" + "\033[0m")
    while True:
        hostname = input("\033[94m" + "Hostname(default: 'eupnea-chromebook'): " + "\033[0m")
        if hostname == "":
            print("Using eupnea-chromebook as hostname")
            hostname = "eupnea-chromebook"
            break
        if hostname[0] == "-":
            print("\033[93m" + "Hostname cannot start with a '-'" + "\033[0m")
            continue
        for char in hostname:
            if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
                print("\033[93m" + "Hostname contains invalid character: " + char + "\033[0m")
                break
        else:
            break

    print(
        "\033[92m" + "Would you like to rebind the Search/Super/Win key to Caps Lock?(NOT RECOMMENDED)" + "\033[0m")
    if input("\033[94m" + "Type yes to rebind. Press enter to keep old binding" "\033[0m" + "\n") == "yes":
        print("Search key will be a CAPS LOCK key")
        rebind_search = True
    else:
        print("Search key will be Super/Win key")
        rebind_search = False

    # TODO: Add better device name check
    while True:
        # Print USB devices only
        lsblk_out = bash("lsblk -o NAME,MODEL,SIZE,TRAN").splitlines()
        found_usb = False
        for line in lsblk_out[2:]:
            if not line.find("usb") == -1:
                print(line[:-3])
                found_usb = True
        if not found_usb:
            print("\033[92m" + 'No available USBs/SD-cards found. Building image file.' + "\033[0m" + "\n")
            device = "image"
            break
        else:
            device = input("\033[92m" + 'Enter usb/sdcard name(example: sdb) or "image" to build an image'
                           + "\033[0m" + "\n").strip()
            if device == "image":
                create_iso = True
                print("Building image instead of writing directly")
                break
            elif device == "":
                print("\033[93m" + "Device name cannot be empty" + "\033[0m")
            else:
                create_iso = False
                print(f"Writing directly to /dev/{device}")
                break

    print("User input complete")
    return distro_name, distro_version, distro_link, de_name, device, username, password, hostname, rebind_search, \
           create_iso


if __name__ == "__main__":
    print("\033[91m" + "Do not run this file. Run build.py" + "\033[0m")
