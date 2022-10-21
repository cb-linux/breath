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
    chroot("dnf install -y git vboot-utils")  # postinstall dependencies
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
        case "deepin":
            print_status("Installing deepin")
            chroot("dnf group install -y 'Deepin Desktop'")
        case "budgie":
            print_error("Budgie is not available for Fedora")
            exit(1)
        case "cli":
            print_status("Skipping desktop environment install")
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)
    stop_progress()  # stop fake progress

    if not de_name == "cli":
        # Set system to boot to gui
        chroot("systemctl set-default graphical.target")
    print_status("Desktop environment setup complete")

    # Relabel all files for SELinux
    # If this is not done, the system won't let users login, even if set to permissive
    # copy /proc files needed for fixfiles
    mkdir("/mnt/depthboot/proc/self")
    cpfile("configs/selinux/mounts", "/mnt/depthboot/proc/self/mounts")
    cpfile("configs/selinux/mountinfo", "/mnt/depthboot/proc/self/mountinfo")
    # copy /sys files needed for fixfiles
    mkdir("/mnt/depthboot/sys/fs/selinux/initial_contexts/", create_parents=True)
    cpfile("configs/selinux/unlabeled", "/mnt/depthboot/sys/fs/selinux/initial_contexts/unlabeled")
    try:
        chroot("/sbin/fixfiles -T 0 restore")
    except subprocess.CalledProcessError:
        pass  # due to working in a chroot, fixfiles fails at the end, but the files are still relabeled

    # Add depthboot to version(this is purely cosmetic)
    with open("/mnt/depthboot/etc/os-release", "r") as f:
        os_release = f.read()
    os_release = os_release.replace("(Generic)", "Depthboot")
    with open("/mnt/depthboot/etc/os-release", "w") as f:
        f.write(os_release)

    print_status("Fedora setup complete")


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')
    else:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
