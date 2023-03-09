from functions import *
from urllib.request import urlretrieve


def config(de_name: str, distro_version: str, verbose: bool, kernel_version: str) -> None:
    set_verbose(verbose)
    print_status("Configuring Pop!_OS")

    print_status("Removing casper debs")  # Source : https://github.com/pop-os/distinst
    chroot("apt-get purge -y btrfs-progs casper cifs-utils distinst distinst-v2 dmraid expect f2fs-tools fatresize "
           "gettext gparted gparted-common grub-common grub2-common kpartx kpartx-boot libdistinst libdmraid1.0.0.rc16"
           " libinih1 libnss-mymachines localechooser-data os-prober pop-installer pop-installer-casper pop-shop-casper"
           " squashfs-tools systemd-container tcl-expect user-setup xfsprogs kernelstub efibootmgr")
    # Add eupnea repo
    mkdir("/mnt/depthboot/usr/local/share/keyrings", create_parents=True)
    # download public key
    urlretrieve("https://eupnea-linux.github.io/apt-repo/public.key",
                filename="/mnt/depthboot/usr/local/share/keyrings/eupnea.key")
    with open("/mnt/depthboot/etc/apt/sources.list.d/eupnea.list", "w") as file:
        file.write("deb [signed-by=/usr/local/share/keyrings/eupnea.key] https://eupnea-linux.github.io/"
                   "apt-repo/debian_ubuntu jammy main")
    # update apt
    chroot("apt-get update -y")

    # system76-acpi-dkms is preinstalled but needs an update
    # The apt postinstall of system76-acpi-dkms tries to run update-initramfs which is not possible in a chroot ->
    # reinstall system76-acpi-dkms to ignore the postinstall script
    print_status("Reinstalling system76-acpi-dkms, ignore apt errors")
    # remove postinstall script as it will fail if run inside a chroot
    rmfile("/mnt/depthboot/var/lib/dpkg/info/system76-acpi-dkms.prerm")
    chroot("sudo apt-get remove -y system76-acpi-dkms")
    with contextlib.suppress(subprocess.CalledProcessError):
        chroot("sudo apt-get install -y system76-acpi-dkms")
    # Edit the postinstall script to force success
    with open("/mnt/depthboot/var/lib/dpkg/info/system76-acpi-dkms.postinst", "r") as file:
        config = file.read()
    with open("/mnt/depthboot/var/lib/dpkg/info/system76-acpi-dkms.postinst", "w") as file:
        file.write("#!/bin/sh\nexit 0\n")
    # Rerun dpkg configuration for package to be recognized as installed
    chroot("dpkg --configure system76-acpi-dkms")
    # Restore postinstall script
    with open("/mnt/depthboot/var/lib/dpkg/info/system76-acpi-dkms.postinst", "w") as file:
        file.write(config)

    chroot("apt-get upgrade -y")
    # Install general dependencies + eupnea packages
    chroot("apt-get install -y eupnea-utils eupnea-system")

    # Install kernel
    if kernel_version == "mainline":
        chroot("apt-get install -y eupnea-mainline-kernel")
    elif kernel_version == "chromeos":
        chroot("apt-get install -y eupnea-chromeos-kernel")

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
