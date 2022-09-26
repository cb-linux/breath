#!/usr/bin/env python3

import os
import sys
from typing import Tuple
from urllib.request import urlretrieve
from urllib.error import URLError
from threading import Thread
from time import sleep
import json

from functions import *


# Clean /tmp from eupnea files
def prepare_host(de_name: str) -> None:
    print("\033[96m" + "Preparing host system" + "\033[0m")

    # umount fedora temp if exists
    try:
        bash("umount -lf /tmp/eupnea-build/fedora-tmp-mnt 2>/dev/null")
    except subprocess.CalledProcessError:
        pass

    print("Creating /tmp/eupnea-build")
    rmdir("/tmp/eupnea-build")
    mkdir("/tmp/eupnea-build", True)

    print("Creating mnt point")
    try:
        bash("umount -lf /mnt/eupnea 2>/dev/null")  # just in case
    except subprocess.CalledProcessError:
        print("Failed to unmount /mnt/eupnea, ignoring")
        pass
    rmdir("/mnt/eupnea")
    mkdir("/mnt/eupnea", True)

    print("Removing old files if they exist")
    rmfile("eupnea.img")
    rmfile("kernel.flags")

    print("Installing necessary packages")
    # install cgpt and futility
    # TODO: Properly check if packages are installed
    if path_exists("/usr/bin/apt"):
        bash("apt-get install cgpt vboot-kernel-utils -y")
    # arch packages are installed before elevating to root
    elif path_exists("/usr/bin/dnf"):
        bash("dnf install cgpt vboot-utils --assumeyes")

    # install debootstrap for debian
    if de_name == "debian":
        if path_exists("/usr/bin/apt"):
            bash("apt-get install debootstrap -y")
        elif path_exists("/usr/bin/pacman"):
            bash("pacman -S debootstrap --noconfirm")
        elif path_exists("/usr/bin/dnf"):
            bash("dnf install debootstrap --assumeyes")
        else:
            print("\033[91m" + "Debootstrap not found, please install it using your disotros package manager or select"
                  + " another distro instead of debian" + "\033[0m")
            exit(1)

    # install arch-chroot for arch
    elif de_name == "arch":
        if path_exists("/usr/bin/apt"):
            bash("apt-get install arch-install-scripts -y")
        elif path_exists("/usr/bin/pacman"):
            bash("pacman -S arch-install-scripts --noconfirm")
        elif path_exists("/usr/bin/dnf"):
            bash("dnf install arch-install-scripts --assumeyes")
        else:
            print(
                "\033[91m" + "Arch-install-scripts not found, please install it using your disotros package manager" +
                " or select another distro instead of arch" + "\033[0m")
            exit(1)


# download kernel files from GitHub
def download_kernel(kernel_type: str, dev_release: bool, main_pid: int) -> None:
    print("\033[96m" + "Downloading kernel binaries from github" + "\033[0m")
    # select correct link
    if dev_release:
        url = "https://github.com/eupnea-linux/kernel/releases/download/dev-build/"
    else:
        url = "https://github.com/eupnea-linux/kernel/releases/latest/download/"

    # download kernel files
    try:
        match kernel_type:
            case "mainline":
                url = "https://github.com/eupnea-linux/mainline-kernel/releases/latest/download/"
                urlretrieve(f"{url}bzImage", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
                urlretrieve(f"{url}headers.tar.xz", filename="/tmp/eupnea-build/headers.tar.xz")
            case "alt":
                print("Downloading alt kernel")
                urlretrieve(f"{url}bzImage-alt", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules-alt.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
            case "exp":
                print("Downloading experimental 5.15 kernel")
                urlretrieve(f"{url}bzImage-exp", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules-exp.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
            case "stable":
                urlretrieve(f"{url}bzImage", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
    except URLError:
        print("\033[91m" + "Failed to reach github. Check your internet connection and try again" + "\033[0m")
        bash(f"kill {main_pid}")


# Prepare USB, usb is not yet fully implemented
def prepare_usb(device: str) -> Tuple[str, str]:
    print("\033[96m" + "Preparing USB" + "\033[0m")

    # fix device name if needed
    if device.endswith("/") or device.endswith("1") or device.endswith("2"):
        device = device[:-1]
    # add /dev/ to device name, if needed
    if not device.startswith("/dev/"):
        device = f"/dev/{device}"

    # unmount all partitions
    try:
        bash(f"umount -lf {device}* 2>/dev/null")
    except subprocess.CalledProcessError:
        pass
    return partition(device, True)


# Create, mount, partition the img and flash the eupnea kernel
def prepare_img() -> Tuple[str, str]:
    print("\033[96m" + "Preparing img" + "\033[0m")

    print("Allocating space for image, might take a while")
    # try fallocate, if it fails use dd
    # TODO: determine img size
    img_size = 10  # 10 for now
    if not bash(f"fallocate -l {img_size}G eupnea.img") == "":
        bash("dd if=/dev/zero of=eupnea.img status=progress bs=12884 count=1000070")

    print("Mounting empty image")
    mnt_point = bash("losetup -f --show eupnea.img")
    if mnt_point == "":
        print("\033[91m" + "Failed to mount image" + "\033[0m")
        exit(1)
    print("Image mounted at" + mnt_point)
    return partition(mnt_point, False)


def partition(mnt_point: str, write_usb: bool) -> Tuple[str, str]:
    # remove partition table from usb
    if write_usb:
        bash(f"wipefs -af {mnt_point}")

    # format as per depthcharge requirements,
    # READ: https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices
    print("Partitioning mounted image and adding flags")
    bash(f"parted -s {mnt_point} mklabel gpt")
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Kernel 1 65")  # kernel partition
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Root 65 100%")  # rootfs partition
    bash(f"cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 {mnt_point}")  # depthcharge flags

    # get uuid of rootfs partition
    if write_usb:
        # if writing to usb, then no p in partition name
        rootfs_partuuid = bash(f"blkid -o value -s PARTUUID {mnt_point}2")
    else:
        rootfs_partuuid = bash(f"blkid -o value -s PARTUUID {mnt_point}p2")
    if rootfs_partuuid == "":
        print("\033[91m" + "Failed to get rootfs partition uuid" + "\033[0m")
        exit(1)
    # read and modify kernel flags
    with open("configs/kernel.flags", "r") as flags:
        temp = flags.read().replace("${USB_ROOTFS}", rootfs_partuuid).strip()
    with open("kernel.flags", "w") as config:
        config.write(temp)

    print("Signing kernel")
    bash("futility vbutil_kernel --arch x86_64 --version 1 --keyblock /usr/share/vboot/devkeys/kernel.keyblock"
         + " --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk --bootloader kernel.flags" +
         " --config kernel.flags --vmlinuz /tmp/eupnea-build/bzImage --pack /tmp/eupnea-build/bzImage.signed")

    print("Flashing kernel")
    if write_usb:
        # if writing to usb, then no p in partition name
        bash(f"dd if=/tmp/eupnea-build/bzImage.signed of={mnt_point}1")
    else:
        bash(f"dd if=/tmp/eupnea-build/bzImage.signed of={mnt_point}p1")

    print("Creating rootfs")
    if write_usb:
        # if writing to usb, then no p in partition name
        bash(f"yes 2>/dev/null | mkfs.ext4 {mnt_point}2")  # 2>/dev/null is to supress yes broken pipe warning
    else:
        bash(f"yes 2>/dev/null | mkfs.ext4 {mnt_point}p2")  # 2>/dev/null is to supress yes broken pipe warning

    print("Mounting rootfs to /mnt/eupnea")
    if write_usb:
        # if writing to usb, then no p in partition name
        bash(f"mount {mnt_point}2 /mnt/eupnea")
    else:
        bash(f"mount {mnt_point}p2 /mnt/eupnea")
    return mnt_point, rootfs_partuuid  # return loop device, so it can be unmounted at the end


# download the distro rootfs
def download_rootfs(distro_name: str, distro_version: str, distro_link: str, main_pid: int) -> None:
    print("\033[96m" + "Downloading rootfs." + "\033[0m")
    try:
        match distro_name:
            case "ubuntu":
                print(f"Downloading ubuntu rootfs {distro_version}")
                urlretrieve(
                    f"https://cloud-images.ubuntu.com/releases/{distro_version}/release/ubuntu-{distro_version}"
                    f"-server-cloudimg-amd64-root.tar.xz",
                    filename="/tmp/eupnea-build/ubuntu-rootfs.tar.xz")
            case "debian":
                print("Downloading debian with debootstrap")
                # Debian sometimes fails for no apparent reason, so we try 2 times
                debian_result = bash(
                    "debootstrap stable /tmp/eupnea-build/debian https://deb.debian.org/debian/")
                if debian_result.__contains__("Couldn't download packages:"):
                    print("\033[91m\nDebootstrap failed, retrying once\n\033[0m")
                    # delete the failed rootfs
                    rmdir("/tmp/eupnea-build/debian")
                    debian_result = bash(
                        "debootstrap stable /tmp/eupnea-build/debian https://deb.debian.org/debian/")
                    if debian_result.__contains__("Couldn't download packages:"):
                        print("\033[91m\nDebootstrap failed again, check your internet connection or try again later" +
                              "\033[0m")
                        bash(f"kill {main_pid}")
            case "arch":
                print("Downloading latest arch rootfs")
                urlretrieve(distro_link, filename="/tmp/eupnea-build/arch-rootfs.tar.gz")
            case "fedora":
                print(f"Downloading fedora rootfs version: {distro_version}")
                urlretrieve(distro_link, filename="/tmp/eupnea-build/fedora-rootfs.raw.xz")
    except URLError:
        print(
            "\033[91m" + "Couldn't download rootfs. Check your internet connection and try again. If the error" +
            " persists, create an issue with the distro and version in the name" + "\033[0m")
        bash(f"kill {main_pid}")  # kill main thread, as this function running in a different thread


# Download Wi-Fi firmware for later
def download_firmware(main_pid: int) -> None:
    print("Downloading firmware")
    try:
        bash("git clone https://chromium.googlesource.com/chromiumos/third_party/linux-firmware/ "
             "/tmp/eupnea-build/firmware")
    except URLError:
        print("\033[91m" + "Couldn't download firmware. Check your internet connection and try again." + "\033[0m")
        bash(f"kill {main_pid}")


# extract the rootfs to the img
def extract_rootfs(distro_name: str, main_pid: int) -> None:
    print("\033[96m" + "Extracting rootfs" + "\033[0m")
    match distro_name:
        case "ubuntu":
            print("Extracting ubuntu rootfs")
            bash("tar xfp /tmp/eupnea-build/ubuntu-rootfs.tar.xz -C /mnt/eupnea --checkpoint=.10000")
        case "debian":
            print("Copying debian rootfs")
            cpdir("/tmp/eupnea-build/debian/", "/mnt/eupnea/")
        case "arch":
            print("Extracting arch rootfs")
            mkdir("/tmp/eupnea-build/arch-rootfs")
            bash("tar xfp /tmp/eupnea-build/arch-rootfs.tar.gz -C /tmp/eupnea-build/arch-rootfs --checkpoint=.10000")
            cpdir("/tmp/eupnea-build/arch-rootfs/root.x86_64/", "/mnt/eupnea/")

        case "fedora":
            print("Extracting fedora rootfs")
            # extract to temp location, find rootfs and extract it to mounted image
            mkdir("/tmp/eupnea-build/fedora-tmp-mnt")
            # using unxz instead of tar
            bash("unxz -d /tmp/eupnea-build/fedora-rootfs.raw.xz -c > /tmp/eupnea-build/fedora-raw")

            # mount fedora raw image
            fedora_root_part = bash("losetup -P -f --show /tmp/eupnea-build/fedora-raw") + "p5"
            if fedora_root_part == "":
                print("\033[91m" + "Couldn't mount fedora image with losetup" + "\033[0m")
                bash(f"kill {main_pid}")
            bash(
                f"mount {fedora_root_part} /tmp/eupnea-build/fedora-tmp-mnt")  # return to check for mount errors
            # copy actual root file to eupnea mount
            print("Copying fedora rootfs to /mnt/eupnea")
            # TODO: Fix python copying
            bash("cp -rp /tmp/eupnea-build/fedora-tmp-mnt/root/* /mnt/eupnea/")  # python fails to copy

            # unmount fedora image to prevent errors
            bash(f"umount -fl /tmp/eupnea-build/fedora-tmp-mnt")
            bash(f"losetup -d {fedora_root_part[:-2]}")


# Configure distro agnostic options
def post_extract(username: str, password: str, hostname: str, distro_name: str, de_name: str, kernel_type: str) -> None:
    print("\n\033[96m" + "Configuring Eupnea" + "\033[0m")

    print("Copying resolv.conf")
    # delete broken symlink
    rmfile("/mnt/eupnea/etc/resolv.conf", True)
    cpfile("/etc/resolv.conf", "/mnt/eupnea/etc/resolv.conf")

    print("Extracting kernel modules")
    bash("rm -rf /mnt/eupnea/lib/modules/*")  # delete old modules

    # modules tar contains /lib/modules, so it's extracted to / and --skip-old-files is used to prevent overwriting
    # other files in /lib
    bash("tar xpf /tmp/eupnea-build/modules.tar.xz --skip-old-files -C /mnt/eupnea/ --checkpoint=.10000")
    print("")  # break line after tar

    if not (distro_name == "ubuntu" and de_name == "gnome"):  # Ubuntu + gnome has first time setup
        print("Configuring user")
        chroot(f"useradd --create-home --shell /bin/bash {username}")
        chroot(f'echo "{username}:{password}" | chpasswd')
        match distro_name:
            case "ubuntu" | "debian":
                chroot(f"usermod -aG sudo {username}")
            case "arch" | "fedora":
                chroot(f"usermod -aG wheel {username}")

    print("Extracting kernel headers")
    # TODO: extract kernel headers

    print("Setting hostname")
    with open("/mnt/eupnea/etc/hostname", "w") as hostname_file:
        hostname_file.write(hostname)

    print("Copying eupnea scripts")
    cpdir("postinstall-scripts", "/mnt/eupnea/usr/local/bin/")
    chroot("chmod 755 /usr/local/bin/*")  # make scripts executable in system
    cpfile("functions.py", "/mnt/eupnea/usr/local/bin/functions.py")

    mkdir("/mnt/eupnea/usr/local/eupnea-configs")
    cpdir("configs", "/mnt/eupnea/usr/local/eupnea-configs")

    # create settings file
    print("Creating eupnea settings file")
    with open("configs/eupnea-settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    settings["kernel_type"] = kernel_type
    with open("/mnt/eupnea/usr/local/eupnea-settings.json", "w") as settings_file:
        json.dump(settings, settings_file)

    print("Configuring sleep")
    # disable hibernation aka S4 sleep, READ: https://eupnea-linux.github.io/docs.html#/bootlock
    # TODO: Fix sleep
    mkdir("/mnt/eupnea/etc/systemd/")  # just in case systemd path doesn't exist
    with open("/mnt/eupnea/etc/systemd/sleep.conf", "a") as conf:
        conf.write("SuspendState=freeze\nHibernateState=freeze")

    print("Adding kernel modules")
    # Enable loading modules needed for eupnea
    cpfile("configs/eupnea-modules.conf", "/mnt/eupnea/etc/modules-load.d/eupnea-modules.conf")

    # TODO: Fix failing services
    # The services below fail to start, so they are disabled
    # ssh
    rmfile("/mnt/eupnea/etc/systemd/system/multi-user.target.wants/ssh.service")
    rmfile("/mnt/eupnea/etc/systemd/system/sshd.service")


# post extract and distro config
def post_config(rebind_search: bool):
    # Add chromebook layout. Needs to be done after install Xorg/Wayland
    print("Backing up default keymap and setting Chromebook layout")
    cpfile("/mnt/eupnea/usr/share/X11/xkb/symbols/pc", "/mnt/eupnea/usr/share/X11/xkb/symbols/pc.default")
    cpfile("configs/xkb/xkb.chromebook", "/mnt/eupnea/usr/share/X11/xkb/symbols/pc")
    if rebind_search:  # rebind search key to caps lock
        print("Rebinding search key to Caps Lock")
        cpfile("/mnt/eupnea/usr/share/X11/xkb/keycodes/evdev", "/mnt/eupnea/usr/share/X11/xkb/keycodes/evdev.default")

    # Add postinstall service
    print("Adding postinstall service")
    cpfile("configs/postinstall.service", "/mnt/eupnea/etc/systemd/system/postinstall.service")
    chroot("systemctl enable postinstall.service")

    # copy previously downloaded firmware
    print("Copying google firmware")
    rmdir("/mnt/eupnea/lib/firmware")
    cpdir("/tmp/eupnea-build/firmware", "/mnt/eupnea/lib/firmware")


# chroot command
def chroot(command: str) -> str:
    return bash(f'chroot /mnt/eupnea /bin/sh -c "{command}"')


# The main build script
def start_build(args, build_options):
    # Install arch packages from AUR, before elevating to root
    if path_exists("/usr/bin/pacman"):
        if input("Following packages are required to install Eupnea: cgpt-bin and vboot-utils. Install them now? "
                 "(y/n)").lower() == "y":
            bash("pacman -S --needed base-devel --noconfirm")

            bash("git clone https://aur.archlinux.org/cgpt-bin.git")
            cpfile("configs/PKGBUILD", "cgpt-bin/PKGBUILD")
            bash("cd cgpt-bin && makepkg -sirc --noconfirm")

            bash("git clone https://aur.archlinux.org/vboot-utils.git")
            bash("cd vboot-utils && makepkg -sirc --noconfirm")

            rmdir("cgpt-bin", keep_dir=False)
            rmdir("vboot-utils", keep_dir=False)
        else:
            print("\033[91m" + "Please install cgpt and vboot-utils and restart the script" + "\033[0m")
            print("Continuing")

    # Elevate script to root
    if not os.geteuid() == 0:
        sudo_args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)

    main_thread_pid = os.getpid()  # for threads to be able to kill main thread

    dev_release = False
    kernel_type = "stable"
    if args.dev_build:
        print("\033[93m" + "Using dev release" + "\033[0m")
        dev_release = True
    if args.alt:
        print("\033[93m" + "Using alt kernel" + "\033[0m")
        kernel_type = "alt"
    if args.exp:
        print("\033[93m" + "Using experimental kernel" + "\033[0m")
        kernel_type = "exp"
    if args.mainline:
        print("\033[93m" + "Using mainline kernel" + "\033[0m")
        kernel_type = "mainline"
    if args.local_path:
        print("\033[93m" + "Using local files" + "\033[0m")
    if args.verbose:
        print("\033[93m" + "Verbosity increased" + "\033[0m")
        enable_verbose()  # enable verbose output in functions.py

    prepare_host(build_options[0])

    if args.local_path is None:
        # Print kernel download progress in terminal
        kernel_download = Thread(target=download_kernel, args=(kernel_type, dev_release, main_thread_pid,), daemon=True)
        kernel_download.start()
        sleep(1)  # wait for thread to print info
        while kernel_download.is_alive():
            print(".", end="", flush=True)
            sleep(1)
        print("")  # break line

        # Print rootfs download progress in terminal
        rootfs_download = Thread(target=download_rootfs,
                                 args=(build_options[0], build_options[1], build_options[2], main_thread_pid,),
                                 daemon=True)
        rootfs_download.start()
        sleep(1)  # wait for thread to print info
        while rootfs_download.is_alive():
            print(".", end="", flush=True)
            sleep(1)
        print("")  # break line

        # Download firmware
        download_firmware(main_thread_pid)

    else:  # if local path is specified, copy files from there
        if not args.local_path.endswith("/"):
            local_path_posix = f"{args.local_path}/"
        else:
            local_path_posix = args.local_path
        print("\033[96m" + "Copying local files to tmp" + "\033[0m")
        try:
            cpfile(f"{local_path_posix}bzImage", "/tmp/eupnea-build/bzImage")
            cpfile(f"{local_path_posix}modules.tar.xz", "/tmp/eupnea-build/modules.tar.xz")
            cpdir(f"{local_path_posix}firmware", "/mnt/eupnea/lib/firmware/google")
            match build_options[0]:
                case "ubuntu":
                    cpfile(f"{local_path_posix}ubuntu-rootfs.tar.xz", "/tmp/eupnea-build/ubuntu-rootfs.tar.xz")
                case "debian":
                    cpdir(f"{local_path_posix}debian", "/tmp/eupnea-build/debian")
                case "arch":
                    cpfile(f"{local_path_posix}arch-rootfs.tar.gz", "/tmp/eupnea-build/arch-rootfs.tar.gz")
                case "fedora":
                    cpfile(f"{local_path_posix}fedora-rootfs.raw.xz", "/tmp/eupnea-build/fedora-rootfs.raw.xz")
                case _:
                    print("\033[91m" + "Something went **really** wrong!!! (Distro name not found)" + "\033[0m")
                    exit(1)
        except FileNotFoundError:
            print("\033[91m" + "Local rootfs file not found, please verify the file name is correct" + "\033[0m")
            exit(1)

    if build_options[9]:
        output_temp = prepare_img()
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]
    else:
        output_temp = prepare_usb(build_options[4])
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]

    extract_rootfs(build_options[0], main_thread_pid)
    post_extract(build_options[5], build_options[6], build_options[7], build_options[0], build_options[3], kernel_type)

    match build_options[0]:
        case "ubuntu":
            import distro.ubuntu as distro
        case "debian":
            import distro.debian as distro
        case "arch":
            import distro.arch as distro
        case "fedora":
            import distro.fedora as distro
        case _:
            print("\033[91m" + "Something went **really** wrong!!! (Distro name not found)" + "\033[0m")
            exit(1)
    distro.config(build_options[3], build_options[1], root_partuuid, args.verbose)

    post_config(build_options[8])

    # Unmount everything
    print("\033[96m" + "Finishing setup" + "\033[0m")
    print("Unmounting rootfs")
    bash("umount -f /mnt/eupnea")
    if build_options[9]:
        print("Unmounting img")
        bash(f"losetup -d {img_mnt}")
        print("\033[95m" + f"The ready Eupnea image is located at {get_full_path('.')}/eupnea.img" + "\033[0m")
    else:
        print("\033[95m" + "The USB is ready to boot Eupnea. " + "\033[0m")


if __name__ == "__main__":
    print("\033[91m" + "Do not run this file directly. Instead, run main.py" + "\033[0m")
