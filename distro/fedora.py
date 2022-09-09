import os
from os import system as bash
import subprocess as sp


def config(de_name: str, distro_version: str) -> None:
    print("\033[96m" + "Configuring Fedora" + "\033[0m")
    print("Installing packages")
    chroot("dnf update -y")
    chroot("dnf install linux-firmware -y")
    chroot("dnf group install 'Minimal Install' -y; dnf install NetworkManager-tui ncurses -y")
    print("Add nonfree repos")
    chroot("dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-" + distro_version
           + ".noarch.rpm -y")
    print("Disabling plymouth")  # may fail sometimes without error
    chroot("plymouth-set-default-theme details -R &> /dev/null")
    # TODO: Perhaps zram works with mainline?
    chroot("dnf remove zram-generator-defaults -y")  # remove zram as it fails for some reason
    print("\033[96m" + "Downloading and installing DE, might take a while" + "\033[0m")
    match de_name:
        case "gnome":
            print("Installing gnome")
            # As gnome is not preinstalled on the cloud version, we need to install it "manually"
            chroot("dnf inastall @base-x gnome-shell gnome-terminal nautilus firefox chrome-gnome-shell gnome-tweaks " +
                   "@development-tools gnome-terminal-nautilus xdg-user-dirs xdg-user-dirs-gtk gnome-calculator " +
                   "gnome-system-monitor gedit file-roller")
        case "kde":
            print("Installing kde")
            chroot("dnf group install 'KDE Plasma Workspaces' -y")
        case "mate":
            print("Installing mate")
            chroot("dnf group install 'MATE Desktop' -y")
        case "xfce" | "minimal":
            print("Installing xfce")
            chroot("dnf group install 'Xfce Desktop' -y")
        case "lxqt":
            print("Installing lxqt")
            chroot("dnf group install 'LXQt Desktop' -y")
        case "deepin":
            print("Installing deepin")
            chroot("dnf group install 'Deepin Desktop' -y")
        case "budgie":
            print("\033[91m" + "Budgie is not available for Fedora" + "\033[91m")
            exit()
        case "cli":
            print("Installing nothing")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
            exit()
    print("Set SELinux to permissive")
    chroot("sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/sysconfig/selinux")
    print("Fix permissions")  # maybe not needed?
    # chroot("chmod -R 750 /root")


def chroot(command: str) -> str:
    return sp.run('chroot /mnt/eupnea /bin/sh -c "' + command + '"', shell=True, capture_output=True).stdout.decode(
        "utf-8").strip()


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
