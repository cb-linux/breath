from getpass import getpass
from functions import *
from cli_artist import *


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
    print_header("""Welcome to Depthboot, formerly known as Breath
                    This script will create a bootable Linux USB-drive/SD-card/image.
                    The script will now ask a few questions. If you dont know what to answer, just press 'enter' and the
                    recommended answer will be selected.""", flush=True)
    input("Press Enter to continue...")
    while True:
        distro_name  = print_question("Which Linux distro (flavor) would you like to use?", 
                                      options=["Pop!_OS", "Ubuntu", "Fedora", "Debian", "Arch"],
                                      flags=["(default, recommended)"],
                                      print_selection=True,
                                      flush=True)
        match distro_name:
            case "Ubuntu":
                output_dict["distro_name"] = "ubuntu"

                distro_version  = print_question("Which Ubuntu version would you like to use?", 
                                                 options=["22.04", "22.10"],
                                                 flags=["(LTS)", "(latest)"],
                                                 print_selection=True,
                                                 flush=True)
                output_dict["distro_version"] = distro_version
                break

            case "Debian":
                print_warning("Warning: The audio and some postinstall scripts are not supported on debian by default.")
                print_status("Type 'YES' to continue anyways or Press Enter to choose another distro: ")
                if input() == "YES":
                    print_status("'YES' received. Proceed...")
                    output_dict["distro_name"] = "debian"
                    output_dict["distro_version"] = "stable"
                    break
                    # TODO: Add non stable debian versions
                print("Aborting...")
                continue
            case "Arch":
                output_dict["distro_name"] = "arch"
                output_dict["distro_version"] = "latest"
                break
            case "Fedora":
                output_dict["distro_name"] = "fedora"
                distro_version  = print_question("Which Ubuntu version would you like to use?", 
                                                 options=["37", "38"],
                                                 flags=["(stable)", "(latest, beta)"],
                                                 print_selection=True,
                                                 flush=True)
                output_dict["distro_version"] = distro_version
                break
            case "Pop!_OS":  # default
                output_dict["distro_name"] = "pop-os"
                output_dict["distro_version"] = "22.04"
                break

    if output_dict["distro_name"] != "pop-os":
        de_list = ["Gnome", "KDE", "Xfce", "LXQt"]
        flags_list = ["(default, recommended)", "(recommended)", "(recommended for weak devices)", "(recommended for weak devices)"]
    
        match output_dict["distro_name"]:
            case "ubuntu":
                if output_dict["distro_version"] == "22.04":
                    de_list.append("deepin")
            case "debian":
                de_list.append("budgie")
            case "arch":
                de_list.append("deepin")
            case "fedora":
                de_list.extend(["deepin", "budgie"])
        de_list.append("cli")

        while True:
            desktop_env  = print_question("Which desktop environment (Desktop GUI) would you like to use?", 
                                        options=de_list,
                                        flags=flags_list,
                                        print_selection=True,
                                        flush=True)
            if desktop_env == "cli":
                print_warning("Warning: No desktop environment will be installed!")
                print_status("Type 'YES' to continue or Press Enter to choose a desktop environment: ")
                if input() == "YES":
                    print_status("'YES' received. No desktop will be installed. Proceed...")
                    break
                print("Aborting...")
            
            output_dict["de_name"] = desktop_env.lower()
            break
    else:
        # TODO: set to gnome when gnome is fixed
        output_dict["de_name"] = "popos"  # set to gnome

    # Gnome has a first time setup -> skip this part for gnome, as there will be a first time setup
    # TODO: set to gnome when gnome is fixed
    if output_dict["de_name"] != "popos":
        print_question("Enter a username for the new user")
        while True:
            print_status("Username (default: 'localuser'): ")
            output_dict["username"] = input()
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
            print_status("Password: ")
            passwd_temp = getpass()
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
                print_status("Repeat password: ")
                passwd_temp_repeat = getpass()
                if passwd_temp == passwd_temp_repeat:
                    output_dict["password"] = passwd_temp
                    print("Password set")
                    break
                else:
                    print_warning("Passwords do not match, please try again")
                    continue

    print_question("Rebind the Search/Super/Win key to Caps Lock? (NOT RECOMMENDED)")
    print_status("Type 'YES' to rebind. Press enter to keep old binding: ")

    if input() == "YES":
        print_status("'YES' received. Search key will be a CAPS LOCK key. Proceed...")
        rebind_search = True
    else:
        rebind_search = False
    output_dict["rebind_search"] = rebind_search

    while True:
        kernel_type  = print_question("Which kernel type would you like to use? Usually there is no need to change this", 
                                      options=["stable", "experimental", "mainline", "mainline-testing"],
                                      flags=["(default, recommended)", '', "(recommended)", "(not yet supported)"],
                                      print_selection=True,
                                      flush=True)

        if kernel_type == "mainline-testing":
            print_warning("Not yet implemented")
            print("Aborting...")
            continue
        
        output_dict["kernel_type"] = kernel_type.lower()
        break

    if not skip_device:
        print_status("Available devices: ")
        usb_names = []
        usb_info = []
        lsblk_out = bash("lsblk -nd -o NAME,MODEL,SIZE,TRAN").splitlines()
        for line in lsblk_out:
            # MassStorageClass is not a real device, so ignore it
            if not line.find("usb") != -1 and line.find("0B") == -1:  # Print USB devices only with storage
                usb_names.append(line[:3])
                usb_info.append(line[3:])
        if not usb_names:
            print_status("No available USBs/SD-cards found. Building image file.")
        else:
            device = print_question("Select USB-drive/SD-card name or 'image' to build an image",
                                    options=usb_names+["image"],
                                    flags=usb_info+["Image to be flashed"],
                                    print_selection=True,
                                    flush=True)
            if device == "image":
                    print("Building image instead of writing directly")
            else:
                print(f"Writing directly to {device}")
                output_dict["device"] = device

    print_status("User input complete")
    return output_dict
