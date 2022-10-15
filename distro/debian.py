from functions import *


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Debian")

    print_status("Installing dependencies")
    start_progress()  # start fake progress
    # install apt-add-repository
    chroot("apt-get update -y")
    chroot("apt-get install -y software-properties-common")
    # add non-free repos
    chroot("add-apt-repository -y non-free")
    chroot("apt-get update -y")
    # Install dependencies
    chroot("apt-get install -y network-manager sudo firmware-linux-free cloud-utils firmware-linux-nonfree "
           "firmware-iwlwifi iw git")
    stop_progress()  # stop fake progress

    print_status("Downloading and installing de, might take a while")
    start_progress()  # start fake progress
    # DEBIAN_FRONTEND=noninteractive skips locale setup questions
    match de_name:
        case "gnome":
            print_status("Installing GNOME")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y gnome/stable gnome-initial-setup")
        case "kde":
            print_status("Installing KDE")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y task-kde-desktop")
        case "mate":
            print_status("Installing MATE")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y mate-desktop-environment "
                   "mate-desktop-environment-extras gdm3")
        case "xfce":
            print_status("Installing Xfce")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y task-xfce-desktop")
        case "lxqt":
            print_status("Installing LXQt")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y task-lxqt-desktop")
        case "deepin":
            print_error("Deepin is not available for Debian")
            exit(1)
        case "budgie":
            print_status("Installing Budgie")
            chroot("DEBIAN_FRONTEND=noninteractive apt-get install -y budgie-desktop budgie-indicator-applet "
                   "budgie-core lightdm lightdm-gtk-greeter gnome-terminal firefox")
            chroot("systemctl enable lightdm.service")
        case "cli":
            print_status("Skipping desktop environment install")
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)
    stop_progress()  # stop fake progress

    if not de_name == "cli":
        # Set system to boot to gui
        chroot("systemctl set-default graphical.target")

    # GDM3 auto installs gnome-minimal. Gotta remove it if user didn't choose gnome
    if not de_name == "gnome":
        rmfile("/mnt/depthboot/usr/share/xsessions/ubuntu.desktop")
        chroot("apt-get remove -y gnome-shell")
        chroot("apt-get autoremove -y")

    # Fix gdm3, https://askubuntu.com/questions/1239503/ubuntu-20-04-and-20-10-etc-securetty-no-such-file-or-directory
    try:
        cpfile("/mnt/depthboot/usr/share/doc/util-linux/examples/securetty", "/mnt/depthboot/etc/securetty")
    except FileNotFoundError:
        pass
    print_status("Desktop environment setup complete")

    # Replace input-synaptics with newer input-libinput, for better touchpad support
    print_status("Upgrading touchpad drivers")
    chroot("apt-get remove -y xserver-xorg-input-synaptics")
    # chroot("apt-get install -y xserver-xorg-input-libinput")

    # Pre-updating to python3.10 breaks the gnome first time installer...
    '''
    # Pre-update python to 3.10 as some postinstall scripts require it
    print_status("Upgrading python to 3.10")
    # switch to unstable channel
    with open("/mnt/depthboot/etc/apt/sources.list", "r") as file:
        original_sources = file.readlines()
    sources = original_sources
    sources[0] = sources[0].replace("stable", "unstable")
    with open("/mnt/depthboot/etc/apt/sources.list", "w") as file:
        file.writelines(sources)
    # update and install python
    print_status("Installing python 3.10")
    chroot("apt-get update -y")
    chroot("apt-get install -y python3")
    print_status("Python 3.10 installed")
    # revert to stable channel
    with open("/mnt/depthboot/etc/apt/sources.list", "w") as file:
        file.writelines(original_sources)
    chroot("apt-get update -y")
    '''

    # Add depthboot to version(this is purely cosmetic)
    with open("/mnt/depthboot/etc/os-release", "r") as f:
        os_release = f.readlines()
    os_release[0] = os_release[0][:-2] + ' (Depthboot)"\n'
    os_release[1] = os_release[1][:-2] + ' (Depthboot)"\n'
    os_release[3] = os_release[3][:-2] + ' (Depthboot)"\n'
    with open("/mnt/depthboot/etc/os-release", "w") as f:
        f.writelines(os_release)

    print_status("Debian setup complete")


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/depthboot /bin/sh -c "{command}"')
    else:
        bash(f'chroot /mnt/depthboot /bin/sh -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
