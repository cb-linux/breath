from functions import *


def config(de_name: str, distro_version: str, root_partuuid: str, verbose_var: bool) -> None:
    # set verbose var
    global verbose
    verbose = verbose_var

    print("\033[96m" + "Configuring Fedora" + "\033[0m")
    print("Updating packages")
    chroot("dnf update -y")
    
    print("Installing Core packages")
    chroot("dnf group install -y 'Core'")
    
    print("Installing Hardware Support packages")
    chroot("dnf group install -y 'Hardware Support'")
    chroot("dnf group install -y 'Common NetworkManager Submodules'")
    chroot("dnf install -y linux-firmware")
    
    # TODO: Missing the free repos; add extras from a real Fedora install
    print("Add RPMFusion nonfree repo")
    chroot(f"dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{distro_version}"
           f".noarch.rpm -y")
    
    # TODO: Plymouth is never disabled, so why print it? Also, why disabling it?
    #print("Disabling plymouth")  # may fail sometimes without error
    # Disabling plymouth fails too
    # chroot("plymouth-set-default-theme details -R &> /dev/null")
    
    # TODO: Perhaps zram works with mainline?
    chroot("dnf remove zram-generator-defaults -y")  # remove zram as it fails for some reason
    chroot("systemctl disable systemd-zram-setup@zram0.service")  # disable zram service
    
    print("\033[96m" + "Downloading and installing DE, might take a while" + "\033[0m")
    match de_name:
        case "gnome":
            print("Installing GNOME")
            chroot("dnf group install -y 'Fedora Workstation'")
            chroot("systemctl set-default graphical.target")
        case "kde":
            print("Installing KDE")
            chroot("dnf group install -y 'KDE Plasma Workspaces'")
            chroot("systemctl set-default graphical.target")
        case "mate":
            print("Installing MATE")
            chroot("dnf group install -y 'MATE Desktop'")
            chroot("systemctl set-default graphical.target")
        case "xfce":
            print("Installing Xfce")
            chroot("dnf group install -y 'Xfce Desktop'")
            chroot("systemctl set-default graphical.target")
        case "lxqt":
            print("Installing LXQt")
            chroot("dnf group install -y 'LXQt Desktop'")
            chroot("systemctl set-default graphical.target")
        case "deepin":
            print("Installing deepin")
            chroot("dnf group install -y 'Deepin Desktop'")
            chroot("systemctl set-default graphical.target")
        case "budgie":
            print("\033[91m" + "Budgie is not available for Fedora" + "\033[91m")
            exit(1)
        case "cli":
            print("No Desktop Environment will be installed")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
            exit(1)
            
    print("Fixing SELinux")
    # Create /.autorelabel to force SELinux to relabel all files
    with open("/mnt/eupnea/.autorelabel", "w") as f:
        f.write("")

    print("Fixing fstab")
    # The default fstab file has the wrong PARTUUID, so we need to update it
    with open("configs/fstab/fedora.fstab", "r") as f:
        fstab = f.read()
    fstab = fstab.replace("insert_partuuid", root_partuuid)
    with open("/mnt/eupnea/etc/fstab", "w") as f:
        f.write(fstab)

    # Add eupnea to version(this is purely cosmetic)
    with open("/mnt/eupnea/etc/os-release", "r") as f:
        os_release = f.read()
    os_release = os_release.replace("Cloud Edition Prerelease", "Eupnea")
    with open("/mnt/eupnea/etc/os-release", "w") as f:
        f.write(os_release)


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/eupnea /bin/sh -c "{command}"')
    else:
        bash(f'chroot /mnt/eupnea /bin/sh -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
