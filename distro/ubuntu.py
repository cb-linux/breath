from functions import *


def config(de_name: str, distro_version: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)

    print("\033[96m" + "Configuring Ubuntu" + "\033[0m")

    print("Installing packages")
    chroot("apt-get install -y linux-firmware network-manager software-properties-common cloud-utils")

    # TODO: Find out why we need to reinstall dbus
    print("Reinstalling dbus")
    chroot("apt-get reinstall -y dbus")

    # de install fails without updating apt
    print("Updating apt")
    chroot("apt-get update -y")
    print("\033[96m" + "Downloading and installing de, might take a while" + "\033[0m")
    match de_name:
        case "gnome":
            print("Installing gnome")
            chroot("apt-get install -y ubuntu-desktop gnome-software")
        case "kde":
            print("Installing kde")
            chroot("apt-get install -y kde-standard")
        case "mate":
            print("Installing mate")
            chroot("apt-get install -y ubuntu-mate-desktop")
        case "xfce":
            print("Installing xfce")
            chroot("apt-get install -y --no-install-recommends xubuntu-desktop")
            chroot("apt-get install -y xfce4-goodies")
        case "lxqt":
            print("Installing lxqt")
            chroot("apt-get install -y lubuntu-desktop")
        case "deepin":
            print("Installing deepin")
            chroot("add-apt-repository ppa:ubuntudde-dev/stable")
            chroot("apt-get update")
            chroot("apt-get install -y ubuntudde-dde")
        case "budgie":
            print("Installing budgie")
            chroot("apt-get install -y ubuntu-budgie-desktop")
            chroot("dpkg-reconfigure lightdm")
        case "cli":
            print("Installing nothing")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
            exit(1)
    # Ignore libfprint-2-2 fprintd libpam-fprintd errors

    # GDM3 auto installs gnome-minimal. Remove the session link as it's not needed
    if not de_name == "gnome":
        print("Fixing gdm3")
        try:
            rmfile("/mnt/eupnea/usr/share/xsessions/ubuntu.desktop")
        except FileNotFoundError:
            pass
        chroot("apt-get remove -y gnome-shell")
        chroot("apt-get autoremove -y")

    # TODO: Figure out if removing needrestart is necessary
    chroot("apt-get remove -y needrestart")
    print("Fixing securetty if needed")
    try:
        cpfile("/mnt/eupnea/usr/share/doc/util-linux/examples/securetty", "/mnt/eupnea/etc/securetty")
    except FileNotFoundError:
        pass

    print("Fixing fstab")
    # The default fstab file causes systemd-remount-fs to fail
    with open("configs/fstab/ubuntu.fstab", "r") as f:
        fstab = f.read()
    fstab = fstab.replace("insert_partuuid", root_partuuid)
    with open("/mnt/eupnea/etc/fstab", "w") as f:
        f.write(fstab)

    # Replace input-synaptics with newer input-libinput, for better touchpad support
    print("Replacing touchpad drivers")
    chroot("apt-get remove -y xserver-xorg-input-synaptics")
    # chroot("apt-get install -y xserver-xorg-input-libinput")

    # Add eupnea to version(this is purely cosmetic)
    with open("/mnt/eupnea/etc/os-release", "r") as f:
        os_release = f.readlines()
    os_release[1] = os_release[1][:-2] + ' (Eupnea)"\n'
    os_release[4] = os_release[4][:-2] + ' (Eupnea)"\n'
    with open("/mnt/eupnea/etc/os-release", "w") as f:
        f.writelines(os_release)


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/eupnea /bin/sh -c "{command}"')
    else:
        bash(f'chroot /mnt/eupnea /bin/sh -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
