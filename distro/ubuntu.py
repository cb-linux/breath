import contextlib
from urllib.request import urlretrieve
import os
from functions import *


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Ubuntu")

    ubuntu_versions_codenames = {
        "18.04": "bionic",
        "20.04": "focal",
        "21.04": "hirsute",
        "22.04": "jammy",
        "22.10": "kinetic"
    }
    # add missing apt sources
    with open("/mnt/depthboot/etc/apt/sources.list", "a") as file:
        file.write(f"\ndeb http://archive.ubuntu.com/ubuntu {ubuntu_versions_codenames[distro_version]}-backports main "
                   "restricted universe multiverse\n")
        file.write(f"\ndeb http://security.ubuntu.com/ubuntu {ubuntu_versions_codenames[distro_version]}-security main"
                   f" restricted universe multiverse\n")
        file.write(f"\ndeb http://archive.ubuntu.com/ubuntu {ubuntu_versions_codenames[distro_version]}-updates main "
                   f"restricted universe multiverse\n")

    print_status("Installing dependencies")
    # Add eupnea repo
    mkdir("/mnt/depthboot/usr/local/share/keyrings", create_parents=True)
    # download public key
    urlretrieve("https://eupnea-linux.github.io/apt-repo/public.key",
                filename="/mnt/depthboot/usr/local/share/keyrings/eupnea.key")
    with open("/mnt/depthboot/etc/apt/sources.list.d/eupnea.list", "w") as file:
        file.write("deb [signed-by=/usr/local/share/keyrings/eupnea.key] https://eupnea-linux.github.io/"
                   "apt-repo/debian_ubuntu kinetic main")
    # update apt
    chroot("apt-get update -y")
    # Install general dependencies + eupnea packages
    chroot("apt-get install -y linux-firmware network-manager software-properties-common nano git eupnea-utils "
           "eupnea-system")

    print_status("Downloading and installing de, might take a while")
    start_progress()  # start fake progress
    match de_name:
        case "gnome":
            print_status("Installing GNOME")
            chroot(
                "apt-get install -y ubuntu-desktop gnome-software epiphany-browser"
            )
        case "kde":
            print_status("Installing KDE")
            chroot(
                "DEBIAN_FRONTEND=noninteractive apt-get install -y kde-standard plasma-workspace-wayland "
                "sddm-theme-breeze"
            )
        case "xfce":
            print_status("Installing Xfce")
            # install xfce without heavy unnecessary packages
            chroot(
                "apt-get install -y xubuntu-desktop gimp- gnome-font-viewer- gnome-mines- gnome-sudoku- gucharmap-"
                " hexchat- libreoffice-*- mate-calc- pastebinit- synaptic- thunderbird- transmission-gtk-"
            )
            chroot("apt-get install -y nano gnome-software epiphany-browser")
        case "lxqt":
            print_status("Installing LXQt")
            chroot("apt-get install -y lubuntu-desktop discover konqueror")
        case "deepin":
            print_status("Installing deepin")
            chroot("add-apt-repository -y ppa:ubuntudde-dev/stable")
            chroot("apt-get update -y")
            with contextlib.suppress(subprocess.CalledProcessError):
                chroot("apt-get install -y ubuntudde-dde")
            # remove dpkg deepin-anything files to avoid dpkg errors
            # These are later reinstated by the postinstall script
            for file in os.listdir("/mnt/depthboot/var/lib/dpkg/info/"):
                if file.startswith("deepin-anything-"):
                    rmfile(f"/mnt/depthboot/var/lib/dpkg/info/{file}")
            chroot("apt-get install -y discover konqueror")
        case "budgie":
            print_status("Installing Budgie")
            # do not install tex-common, it breaks the installation
            chroot(
                "DEBIAN_FRONTEND=noninteractive apt-get install -y lightdm lightdm-gtk-greeter ubuntu-budgie-desktop"
                " tex-common-"
            )
        case "cli":
            print_status("Skipping desktop environment install")
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)
    stop_progress()  # stop fake progress

    # GDM3 auto installs gnome-minimal. Gotta remove it if user didn't choose gnome
    if de_name != "gnome":
        rmfile("/mnt/depthboot/usr/share/xsessions/ubuntu.desktop")
        chroot("apt-get remove -y gnome-shell")
        chroot("apt-get autoremove -y")

    # Fix gdm3, https://askubuntu.com/questions/1239503/ubuntu-20-04-and-20-10-etc-securetty-no-such-file-or-directory
    with contextlib.suppress(FileNotFoundError):
        cpfile("/mnt/depthboot/usr/share/doc/util-linux/examples/securetty", "/mnt/depthboot/etc/securetty")
    print_status("Desktop environment setup complete")

    # Replace input-synaptics with newer input-libinput, for better touchpad support
    print_status("Upgrading touchpad drivers")
    chroot("apt-get remove -y xserver-xorg-input-synaptics")
    chroot("apt-get install -y xserver-xorg-input-libinput")

    print_status("Ubuntu setup complete")


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')
    else:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
