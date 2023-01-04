from functions import *
from urllib.request import urlretrieve


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Pop!_OS")

    print_status("Removing casper debs")  # Source : https://github.com/pop-os/distinst
    chroot("apt-get purge -y btrfs-progs casper cifs-utils distinst distinst-v2 dmraid expect f2fs-tools fatresize "
           "gettext gparted gparted-common grub-common grub2-common kpartx kpartx-boot libdistinst libdmraid1.0.0.rc16"
           " libinih1 libnss-mymachines localechooser-data os-prober pop-installer pop-installer-casper pop-shop-casper"
           " squashfs-tools systemd-container tcl-expect user-setup xfsprogs kernelstub")
    # Add eupnea repo
    mkdir("/mnt/depthboot/usr/local/share/keyrings", create_parents=True)
    # download public key
    urlretrieve("https://eupnea-linux.github.io/apt-repo/public.key",
                filename="/mnt/depthboot/usr/local/share/keyrings/eupnea.key")
    with open("/mnt/depthboot/etc/apt/sources.list.d/eupnea.list", "w") as file:
        file.write("deb [signed-by=/usr/local/share/keyrings/eupnea.key] https://eupnea-linux.github.io/"
                   "apt-repo/debian_ubuntu kinetic main")
    # update apt
    chroot("apt-get update")
    # Install general dependencies + eupnea packages
    chroot("apt-get install -y git pop-gnome-initial-setup eupnea-utils eupnea-system")

    # Replace input-synaptics with newer input-libinput, for better touchpad support
    print_status("Upgrading touchpad drivers")
    chroot("apt-get remove -y xserver-xorg-input-synaptics")
    chroot("apt-get install -y xserver-xorg-input-libinput")

    # Enable wayland
    print_status("Enabling Wayland")
    with open("/mnt/depthboot/etc/gdm3/custom.conf", "r") as file:
        gdm_config = file.read()
    with open("/mnt/depthboot/etc/gdm3/custom.conf", "w") as file:
        file.write(gdm_config.replace("WaylandEnable=false", "#WaylandEnable=false"))
    # TODO: Set wayland as default

    print_status("Pop!_OS setup complete")


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')
    else:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
