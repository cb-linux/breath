from functions import *


def config(de_name: str, distro_version: str, username:str,root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Pop!_OS")

    print_status("Removing casper debs") # src : https://github.com/pop-os/distinst
    chroot("apt-get purge btrfs-progs casper cifs-utils distinst distinst-v2 dmraid expect f2fs-tools fatresize gettext"
           " gparted gparted-common grub-common grub2-common kpartx kpartx-boot libdistinst libdmraid1.0.0.rc16 "
           "libinih1 libnss-mymachines localechooser-data os-prober pop-installer pop-installer-casper pop-shop-casper "
           "squashfs-tools systemd-container tcl-expect user-setup xfsprogs -y")
    chroot("apt-get update")
    chroot("apt-get install cloud-utils -y")

    # Replace input-synaptics with newer input-libinput, for better touchpad support
    print_status("Upgrading touchpad drivers")
    chroot("apt-get remove -y xserver-xorg-input-synaptics")
    chroot("apt-get install -y xserver-xorg-input-libinput")

    # Add depthboot to version(this is purely cosmetic)
    with open("/mnt/depthboot/etc/os-release", "r") as f:
        os_release = f.readlines()
    os_release[1] = os_release[1][:-2] + ' (Depthboot)"\n'
    os_release[4] = os_release[4][:-2] + ' (Depthboot)"\n'
    with open("/mnt/depthboot/etc/os-release", "w") as f:
        f.writelines(os_release)

    print_status("Pop!_OS setup complete")


def chroot(command: str) -> None:
    if verbose:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')
    else:
        bash(f'chroot /mnt/depthboot /bin/bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
