import os
from os import system as bash
import subprocess as sp


def config(de_name: str, distro_version: str) -> None:
    print("\033[96m" + "Configuring Ubuntu" + "\033[0m")
    print("Installing packages")
    chroot("apt install -y linux-firmware network-manager software-properties-common cloud-utils")
    # TODO: Find out why we need to reinstall dbus
    print("Reinstalling dbus")
    chroot("apt reinstall -y dbus")
    # de install fails without updating apt
    print("Updating apt")
    chroot("apt update -y")
    print("\033[96m" + "Downloading and installing de, might take a while" + "\033[0m")
    match de_name:
        case "gnome":
            print("Installing gnome")
            chroot("apt install -y ubuntu-desktop")
        case "kde":
            print("Installing kde")
            chroot("apt install -y kde-standard")
        case "mate":
            print("Installing mate")
            chroot("apt install -y ubuntu-mate-desktop")
        case "xfce":
            print("Installing xfce")
            chroot("apt install -y xubuntu-desktop")
        case "lxqt":
            print("Installing lxqt")
            chroot("apt install -y lubuntu-desktop")
        case "deepin":
            print("Installing deepin")
            chroot("add-apt-repository ppa:ubuntudde-dev/stable")
            chroot("apt update")
            chroot("apt install -y ubuntudde-dde")
        case "budgie":
            print("Installing budgie")
            chroot("apt install -y ubuntu-budgie-desktop")
            chroot("dpkg-reconfigure lightdm")
        case "minimal":
            print("Installing minimal")
            chroot("apt install -y xfce4 xfce4-terminal --no-install-recommends")
        case "cli":
            print("Installing nothing")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
            exit(1)
    # Ignore libfprint-2-2 fprintd libpam-fprintd errors
    # GDM3 auto installs gnome-minimal. Gotta remove it if user didnt choose gnome
    if not de_name == "gnome":
        print("Fixing gdm3")
        try:
            os.remove("/mnt/eupnea/usr/share/xsessions/ubuntu.desktop")
        except FileNotFoundError:
            pass
        chroot("apt remove -y gnome-shell")
        chroot("apt autoremove -y")
    # TODO: Figure out if removing needrestart is necessary
    chroot("apt remove -y needrestart")
    print("Fixing securetty if needed")
    # "2>/dev/null" is for hiding error message, as not to scare the user
    bash("cp /mnt/eupnea/usr/share/doc/util-linux/examples/securetty /mnt/eupnea/etc/securetty 2>/dev/null")


def chroot(command: str) -> str:
    return sp.run('chroot /mnt/eupnea /bin/sh -c "' + command + '"', shell=True, capture_output=True).stdout.decode(
        "utf-8").strip()


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
