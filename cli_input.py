from getpass import getpass
from functions import *


def get_user_input(skip_device: bool = False) -> dict:
    output_dict = {
        "distro_name": "",
        "distro_version": "",
        "de_name": "",
        "username": "localuser",
        "password": "",
        "device": "image",
        "rebind_search": False,
        "kernel_type": ""
    }
    # Print welcome message
    print_header("Welcome to Depthboot, formerly known as Breath")
    print_header("This script will create a bootable Linux USB-drive/SD-card/image.")
    print_header("The script will now ask a few questions. If you dont know what to answer, just press 'enter' and the"
                 " recommended answer will be selected.")
    input("(Press enter to continue)")
    print_question("Which Linux distro(flavor) would you like to use?")
    while True:
        temp_distro_name = input(
            "\033[94m" + "Available options: Pop!_OS(default, recommended), Ubuntu, Fedora, Debian, Arch\n" + "\033[0m")
        match temp_distro_name.lower():
            case "ubuntu":
                output_dict["distro_name"] = "ubuntu"
                while True:
                    print_question("Use latest Ubuntu version?")
                    temp_input = input("\033[94m" + "Press enter for yes(22.10), or type 'LTS' to use the latest "
                                                    "lts version(22.04): " + "\033[0m")
                    if temp_input == "" or temp_input == "22.10":
                        output_dict["distro_version"] = "22.10"
                        print("Using Ubuntu version: " + output_dict["distro_version"])
                        break
                    elif temp_input == "LTS" or temp_input == "lts" or temp_input == "22.04":
                        output_dict["distro_version"] = "22.04"
                        print("Ubuntu: " + output_dict["distro_version"] + " selected")
                        break
                    else:
                        print_warning("Version not available, please choose another")
                        continue
                break
            case "debian":
                print_warning("Warning: The audio and some postinstall scripts are not supported on debian by default.")
                if input("\033[94mType 'yes' to continue anyways or Press Enter to choose another distro" +
                         "\033[0m\n") == "yes":
                    print("Debian stable selected")
                    output_dict["distro_name"] = "debian"
                    output_dict["distro_version"] = "stable"
                    # TODO: Add non stable debian versions
                    break
                continue
            case "arch" | "arch btw":
                print("Arch selected")
                output_dict["distro_name"] = "arch"
                output_dict["distro_version"] = "latest"
                break
            case "fedora":
                output_dict["distro_name"] = "fedora"
                while True:
                    print_question("Use latest stable Fedora version?")
                    temp_input = input("\033[94m" + "Press enter for yes(37), or type 'beta' to use the latest "
                                                    "beta(38):" + "\033[0m")
                    if temp_input == "":
                        output_dict["distro_version"] = "37"
                        print("Using Fedora version: " + output_dict["distro_version"])
                        break
                    elif temp_input == "Beta" or temp_input == "beta":
                        output_dict["distro_version"] = "38"
                        print("Fedora: " + output_dict["distro_version"] + " selected")
                        break
                    else:
                        print_warning("Version not available, please choose another")
                        continue
                break
            case "pop!_os" | "popos" | "pop_os" | "":  # default
                print("Pop!_OS selected")
                output_dict["distro_name"] = "pop-os"
                output_dict["distro_version"] = "22.04"
                break
            case _:
                print_warning("Check your spelling and try again")
                continue

    if not output_dict["distro_name"] == "pop-os":
        print_question("Which desktop environment(Desktop GUI) would you like to use?")
        match output_dict["distro_name"]:
            case "ubuntu":
                available_de = "Gnome(default, recommended), KDE(recommended), Xfce(recommended for weak devices), " \
                               "LXQt(recommended for weak devices), cli"
            case "debian":
                available_de = "Gnome(default, recommended), KDE(recommended), Xfce(recommended for weak device" \
                               "s), LXQt(recommended for weak devices), budgie, cli"
            case "arch":
                available_de = "Gnome(default, recommended), KDE(recommended), Xfce(recommended for weak device" \
                               "s), LXQt(recommended for weak devices), deepin, cli"
            case "fedora":
                available_de = "Gnome(default, recommended), KDE(recommended), Xfce(recommended for weak device" \
                               "s), LXQt(recommended for weak devices), deepin, budgie, cli"

        while True:
            temp_de_name = input("\033[94m" + "Available options: " + available_de + "\033[0m" + "\n")
            match temp_de_name.lower():
                case "gnome" | "":
                    print("Gnome selected")
                    output_dict["de_name"] = "gnome"
                    break
                case "kde":
                    print("KDE selected")
                    output_dict["de_name"] = "kde"
                    break
                case "xfce":
                    print("Xfce selected")
                    output_dict["de_name"] = "xfce"
                    break
                case "lxqt":
                    print("Lxqt selected")
                    output_dict["de_name"] = "lxqt"
                    break
                case "deepin":
                    if output_dict["distro_name"] == "debian":
                        print_warning("Deepin is not available for Debian, please choose another DE")
                    elif output_dict["distro_version"] == "22.10":
                        print_warning("Deepin is not yet available on Ubuntu 22.10, please choose another DE")
                    else:
                        print("Deepin selected")
                        output_dict["de_name"] = "deepin"
                        break
                case "budgie":
                    print("Budgie selected")
                    output_dict["de_name"] = "budgie"
                    break
                case "cli" | "none":
                    print_warning("Warning: No desktop environment will be installed!")
                    if input("\033[94mType 'yes' to continue or Press Enter to choose a desktop environment" +
                             "\033[0m\n") == "yes":
                        print("No desktop will be installed")
                        output_dict["de_name"] = "cli"
                        break
                case _:
                    print_warning("No such Desktop environment. Check your spelling and try again")
    else:
        # TODO: set to gnome when gnome is fixed
        output_dict["de_name"] = "popos"  # set to gnome

    # Gnome has a first time setup -> skip this part for gnome, as there will be a first time setup
    # TODO: set to gnome when gnome is fixed
    if not output_dict["de_name"] == "popos":
        print_question("Enter a username for the new user")
        while True:
            output_dict["username"] = input("\033[94m" + "Username(default: 'localuser'): " + "\033[0m")
            if output_dict["username"] == "":
                print("Using 'localuser' as username")
                output_dict["username"] = "localuser"
                break
            found_invalid_char = False
            for char in output_dict["username"]:
                if char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-":
                    print_warning(f"Username contains invalid character: {char}")
                    found_invalid_char = True
                    break
            if not found_invalid_char:
                print(f"Using {output_dict['username']} as username")
                break

        print_question("Please set a secure password")
        while True:
            passwd_temp = getpass("\033[94m" + "Password: " + "\033[0m")
            if passwd_temp == "":
                print_warning("Password cannot be empty")
                continue

            # temporary fix for ) and ( crashing chpasswd in build.py
            elif passwd_temp.find(")") != -1:
                print_warning("Password cannot contain: )")
                continue
            elif passwd_temp.find("(") != -1:
                print_warning("Password cannot contain: (")
                continue

            else:
                passwd_temp_repeat = getpass("\033[94m" + "Repeat password: " + "\033[0m")
                if passwd_temp == passwd_temp_repeat:
                    output_dict["password"] = passwd_temp
                    print("Password set")
                    break
                else:
                    print_warning("Passwords do not match, please try again")
                    continue

    print_question("Rebind the Search/Super/Win key to Caps Lock?(NOT RECOMMENDED)")
    if input("\033[94m" + "Type yes to rebind. Press enter to keep old binding: " "\033[0m") == "yes":
        print("Search key will be a CAPS LOCK key")
        rebind_search = True
    else:
        print("Search key will be Super/Win key")
        rebind_search = False

    print_question("Which kernel type would you like to use? Usually there is no need to change this")
    while True:
        temp_kernel_type = input("\033[94m" + "Available options: stable(default, recommended), experimental, mainline"
                                              "(recommended), mainline-testing(not yet supported) \n" + "\033[0m")
        match temp_kernel_type.lower():
            case "" | "stable":
                print("Stable kernel selected")
                output_dict["kernel_type"] = "stable"
                break
            case "exp" | "experimental":
                print("Experimental kernel selected")
                output_dict["kernel_type"] = "exp"
                break
            case "main" | "mainline":
                print("Mainline kernel selected")
                output_dict["kernel_type"] = "mainline"
                break
            case "testing" | "mainline-testing":
                print("Mainline testing kernel selected")
                print_warning("Not yet implemented")
                continue
                # TODO: implement mainline testing kernel
                # output_dict["kernel_type"] = "mainline-testing"
                # break
            case _:
                print_warning("Check your spelling and try again")
                continue

    if not skip_device:
        while True:
            print_status("Available devices: ")
            usb_array = []
            lsblk_out = bash("lsblk -nd -o NAME,MODEL,SIZE,TRAN").splitlines()
            for line in lsblk_out:
                # MassStorageClass is not a real device, so ignore it
                if not line.find("usb") == -1 and line.find("0B") == -1:  # Print USB devices only with storage
                    usb_array.append(line[:3])
                    print(line[:-3])  # this is for the user to see the list
            if len(usb_array) == 0:
                print_status("No available USBs/SD-cards found. Building image file.")
                break
            else:
                device = input("\033[92m" + 'Enter USB-drive/SD-card name(example: sdb) or "image" to build an image'
                               + "\033[0m" + "\n").strip()
                if device == "image":
                    print("Building image instead of writing directly")
                    break
                elif device in usb_array:
                    print(f"Writing directly to {device}")
                    output_dict["device"] = device
                    break
                else:
                    print_warning("No such device. Check your spelling and try again")
                    continue

    print_status("User input complete")
    return output_dict
