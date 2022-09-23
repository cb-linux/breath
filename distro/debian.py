from functions import *


def config(de_name: str, distro_version: str, root_partuuid: str, verbose_var: bool) -> None:
    # set verbose var
    global verbose
    verbose = verbose_var

    print("\033[96m" + "Configuring Ubuntu" + "\033[0m")

    print("Installling add-apt-repository")
    chroot("apt-get update -y")
    chroot("apt-get install -y software-properties-common")

    print("Adding non free repos")
    chroot("apt-add-repository non-free")
    chroot("apt-get update -y")

    print("Installing packages")
    chroot("apt-get install -y network-manager sudo firmware-linux-free cloud-utils firmware-linux-nonfree firmware-iwlwifi"
           " iw git")

    print("\033[96m" + "Downloading and installing de, might take a while" + "\033[0m")
    match de_name:
        case "gnome":
            print("Installing gnome")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y gnome/stable gnome-initial-setup")
        case "kde":
            print("Installing kde")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y task-kde-desktop")
        case "mate":
            print("Installing mate")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y mate-desktop-environment "
                   "mate-desktop-environment-extras gdm3")
        case "xfce":
            print("Installing xfce")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y task-xfce-desktop")
        case "lxqt":
            print("Installing lxqt")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y task-lxqt-desktop")
        case "deepin":
            print("\033[91m" + "Deepin is not available for Debian" + "\033[91m")
            exit(1)
        case "budgie":
            print("Installing budgie")
            # DEBIAN_FRONTEND=noninteractive skips locale setup in cli
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y budgie-desktop budgie-indicator-applet "
                   "budgie-core lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "cli":
            print("Installing nothing")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
            exit(1)
    # Ignore libfprint-2-2 fprintd libpam-fprintd errors
    if not de_name == "cli":
        print("Setting system to boot to gui")
        chroot("systemctl set-default graphical.target")
    # GDM3 auto installs gnome-minimal. Gotta remove it if user didnt choose gnome
    if not de_name == "gnome":
        print("Fixing gdm3")
        try:
            rmfile("/mnt/eupnea/usr/share/xsessions/ubuntu.desktop")
        except FileNotFoundError:
            pass
        chroot("apt-get remove -y gnome-shell")
        chroot("apt-get autoremove -y")
    print("Fixing securetty if needed")
    try:
        cpfile("/mnt/eupnea/usr/share/doc/util-linux/examples/securetty", "/mnt/eupnea/etc/securetty")
    except FileNotFoundError:
        pass

    # Add eupnea to version(this is purely cosmetic)
    with open("/mnt/eupnea/etc/os-release", "r") as f:
        os_release = f.readlines()
    os_release[0] = os_release[0][:-2] + ' (Eupnea)"\n'
    os_release[1] = os_release[1][:-2] + ' (Eupnea)"\n'
    os_release[3] = os_release[3][:-2] + ' (Eupnea)"\n'
    with open("/mnt/eupnea/etc/os-release", "w") as f:
        f.writelines(os_release)


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/eupnea /bin/sh -c "{command}"')
    else:
        bash(f'chroot /mnt/eupnea /bin/sh -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
