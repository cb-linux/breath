from functions import *


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Fedora")

    print("Installing dependencies")
    start_progress()  # start fake progress
    chroot(f"dnf install -y --releasever={distro_version} fedora-release")  # update repos list
    # Install core packages
    chroot("dnf group install -y 'Core'")
    # Install firmware packages
    chroot("dnf group install -y 'Hardware Support'")
    chroot("dnf group install -y 'Common NetworkManager Submodules'")
    chroot("dnf install -y linux-firmware")
    chroot("dnf install -y git vboot-utils rsync cloud-utils")  # postinstall dependencies
    # Add RPMFusion repos
    chroot(f"dnf install -y https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-"
           f"{distro_version}.noarch.rpm")
    chroot(f"dnf install -y https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-"
           f"{distro_version}.noarch.rpm")
    stop_progress()  # stop fake progress

    print_status("Downloading and installing DE, might take a while")
    start_progress()  # start fake progress
    match de_name:
        case "gnome":
            print_status("Installing GNOME")
            chroot("dnf group install -y 'Fedora Workstation'")  # Fedora has gnome by default in a workstation install
        case "kde":
            print_status("Installing KDE")
            chroot("dnf group install -y 'KDE Plasma Workspaces'")
            chroot("dnf install -y firefox")
        case "xfce":
            print_status("Installing Xfce")
            chroot("dnf group install -y 'Xfce Desktop'")
            chroot("dnf install -y firefox gnome-software")
        case "lxqt":
            print_status("Installing LXQt")
            chroot("dnf group install -y 'LXQt Desktop'")
            chroot("dnf install -y plasma-discover")
        case "deepin":
            print_status("Installing deepin")
            chroot("dnf group install -y 'Deepin Desktop'")
            chroot("dnf install -y plasma-discover")
        case "budgie":
            print_status("Installing Budgie")
            chroot("dnf install -y budgie-desktop lightdm lightdm-gtk xorg-x11-server-Xorg gnome-terminal firefox "
                   "gnome-software")
        case "cli":
            print_status("Skipping desktop environment install")
            # install network tui
            chroot("dnf install -y NetworkManager-tui")
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)
    stop_progress()  # stop fake progress

    if not de_name == "cli":
        # Set system to boot to gui
        chroot("systemctl set-default graphical.target")
    print_status("Desktop environment setup complete")

    print_status("Adding fedora modules")
    with open("/mnt/depthboot/etc/modules-load.d/eupnea-modules.conf", "a") as f:
        f.write("# Fedora modules\nsunrpc\n")

    print_status("Fedora setup complete")


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')
    else:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
