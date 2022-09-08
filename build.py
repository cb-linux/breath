#!/usr/bin/env python3

import os
from shutil import rmtree as rmdir
from pathlib import Path
import sys
import argparse
import urllib.request
import subprocess as sp
from os import system as bash
import user_input
import urllib.error


# parse arguments from the cli. Only for testing/advanced use. 95% of the arguments are handled by the user_input script
def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--local-path', dest="local_path",
                        help="Local path for kernel files, to use instead of downloading from github." +
                             "(Unsigned kernels only)")
    parser.add_argument("--dev", action="store_true", dest="dev_build", default=False,
                        help="Use latest dev build. May be unstable.")
    parser.add_argument("--alt", action="store_true", dest="alt", default=False,
                        help="Use alt kernel. Only for older devices.")
    parser.add_argument("--exp", action="store_true", dest="exp", default=False,
                        help="Use experimental 5.15 kernel.")
    return parser.parse_args()


# Clean /tmp from eupnea files
def prepare_host(de_name) -> None:
    print("\033[96m" + "Preparing host system" + "\033[0m")
    print("Creating /tmp/eupnea-build")
    bash("umount -f /tmp/eupnea-build/arch")
    rmdir("/tmp/eupnea-build", ignore_errors=True)
    Path("/tmp/eupnea-build/rootfs").mkdir(parents=True)
    print("Creating mnt point")
    bash("umount -lf /mnt/eupnea")  # just in case
    rmdir("/mnt/eupnea", ignore_errors=True)
    Path("/mnt/eupnea").mkdir(parents=True, exist_ok=True)
    print("Installing necessary packages")
    # apt only for now
    # install cgpt and futility
    if sp.run("apt install cgpt vboot-kernel-utils", shell=True, capture_output=True).stdout.decode(
            "utf-8").strip() == "/bin/sh: 1: apt: not found":
        print("\033[91m" + "cgpt and futility not found, please install them using your disotros package manager"
              + "\033[0m")
        exit()
    if de_name == "debian":
        if sp.run("apt install debootstrap", shell=True, capture_output=True).stdout.decode(
                "utf-8").strip() == "/bin/sh: 1: apt: not found":
            print("\033[91m" + "Debootstrap not found, please install it using your disotros package manager"
                  + "\033[0m")
            exit()
    elif de_name == "arch":
        if sp.run("apt install arch-install-scripts", shell=True, capture_output=True).stdout.decode(
                "utf-8").strip() == "/bin/sh: 1: apt: not found":
            print("\033[91m" + "Debootstrap not found, please install it using your disotros package manager"
                  + "\033[0m")
            exit()


# download kernel files from GitHub
def download_kernel(dev_build: bool) -> None:
    print("\033[96m" + "Downloading kernel binaries from the eupnea github" + "\033[0m")
    if dev_build:
        url = "https://github.com/eupnea-linux/kernel/releases/download/dev-build/"
    else:
        url = "https://github.com/eupnea-linux/kernel/releases/latest/download/"
    try:
        if args.alt:
            print("Downloading alt kernel")
            urllib.request.urlretrieve(url + "bzImage.alt", filename="/tmp/eupnea-build/bzImage")
            urllib.request.urlretrieve(url + "modules.alt.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
        elif args.exp:
            print("Downloading experimental 5.15 kernel")
            urllib.request.urlretrieve(url + "bzImage.exp", filename="/tmp/eupnea-build/bzImage")
            urllib.request.urlretrieve(url + "modules.exp.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
        else:
            urllib.request.urlretrieve(url + "bzImage", filename="/tmp/eupnea-build/bzImage")
            urllib.request.urlretrieve(url + "modules.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
    except urllib.error.URLError:
        print("\033[91m" + "Failed to reach github. Check your internet connection and try again" + "\033[0m")
        exit()


# Prepare USB, usb is not yet fully implemented
def prepare_usb() -> None:
    print("\033[96m" + "Preparing USB" + "\033[0m")


# Create, mount, partition the img and flash the eupnea kernel
def prepare_img() -> str:
    print("\033[96m" + "Preparing img" + "\033[0m")
    print("Allocating space for image, might take a while")
    # 12G for now, maybe decrease later
    # try fallocate, if it fails use dd
    if sp.run("fallocate -l 12G eupnea.img", shell=True, capture_output=True).stderr.decode(
            "utf-8").strip() == "/bin/sh: 1: fallocate: not found":
        bash("dd if=/dev/zero of=eupnea.img status=progress bs=12884 count=1000070")
    print("Mounting empty image")
    img_mnt = sp.run(["losetup", "-f", "--show", "eupnea.img"], capture_output=True).stdout.decode("utf-8").strip()
    print("Image mounted at" + img_mnt)
    # format usb as per deptcharge requirements
    print("Partitioning mounted image and adding flags")
    bash("parted -s " + img_mnt + " mklabel gpt")
    bash("parted -s -a optimal " + img_mnt + " unit mib mkpart Kernel 1 65")
    bash("parted -s -a optimal " + img_mnt + " unit mib mkpart Root 65 100%")
    bash("cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 " + img_mnt)
    # get uuid of rootfs partition
    usb_rootfs = sp.run(["blkid", "-o", "value", "-s", "PARTUUID", img_mnt + "p2"], capture_output=True).stdout.decode(
        "utf-8").strip()
    # read and modify kernel flags
    with open("configs/kernel.flags", "r") as file:
        temp = file.read().replace("${USB_ROOTFS}", usb_rootfs).strip()
    with open("kernel.flags", "w") as file:
        file.write(temp)
    print("Signing kernel")
    bash("futility vbutil_kernel --arch x86_64 --version 1 --keyblock /usr/share/vboot/devkeys/kernel.keyblock"
         + " --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk --bootloader kernel.flags" +
         " --config kernel.flags --vmlinuz /tmp/eupnea-build/bzImage --pack /tmp/eupnea-build/bzImage.signed")
    print("Flashing kernel")
    bash("dd if=/tmp/eupnea-build/bzImage.signed of=" + img_mnt + "p1")
    print("Formating rootfs")
    bash("yes | mkfs.ext4 " + img_mnt + "p2")
    print("Mounting rootfs to /mnt/eupnea")
    bash("mount " + img_mnt + "p2 /mnt/eupnea")
    return img_mnt


# download the distro rootfs
def download_rootfs(distro_name: str, distro_version: str, distro_link: str) -> None:
    print("\033[96m" + "Downlaoding rootfs. Do not panick if script seems stuck" + "\033[0m")
    # TODO: Add progress bar or something
    try:
        match distro_name:
            case "ubuntu":
                print("Downloading ubuntu rootfs " + distro_version)
                urllib.request.urlretrieve(
                    "https://cloud-images.ubuntu.com/releases/" + distro_version + "/release/ubuntu-"
                    + distro_version + "-server-cloudimg-amd64-root.tar.xz",
                    filename="/tmp/eupnea-build/rootfs/ubuntu-rootfs.tar.xz")
            case "debian":
                print("Downloading debian with debootstrap")
                bash("debootstrap stable /tmp/eupnea-build/rootfs https://deb.debian.org/debian/")
                pass
            case "arch":
                print("Downloading latest arch rootfs")
                urllib.request.urlretrieve(
                    "https://mirror.rackspace.com/archlinux/iso/latest/archlinux-bootstrap-x86_64.tar.gz",
                    filename="/tmp/eupnea-build/rootfs/arch-rootfs.tar.gz")
            case "fedora":
                print("Downloading fedora rootfs version: " + distro_version)
                urllib.request.urlretrieve(distro_link, filename="/tmp/eupnea-build/rootfs/fedora-rootfs.tar.xz")
    except urllib.error.URLError:
        print(
            "\033[91m" + "Failed to download rootfs. Check your internet connection and try again. If the error" +
            " persists, create an issue with the distro and version in the name" + "\033[0m")
        exit()


# extract the rootfs to the img
def extract_rootfs(distro: str) -> None:
    print("\033[96m" + "Extracting rootfs" + "\033[0m")
    match distro:
        case "ubuntu":
            print("Extracting ubuntu rootfs")
            bash("tar xfp /tmp/eupnea-build/rootfs/ubuntu-rootfs.tar.xz -C " + "/mnt/eupnea --checkpoint=.10000")
        case "debian":
            print("Copying debian rootfs")
            bash("cp -r -p /tmp/eupnea-build/rootfs/* /mnt/eupnea/")
        case "arch":
            print("Extracting arch rootfs")
            # TODO: Figure out how to extract arch rootfs without cd
            # temp chdir into mounted image, then go back to original dir
            temp_path = os.getcwd()
            os.chdir("/mnt/eupnea")
            bash("tar xvpfz /tmp/eupnea-build/rootfs/arch-rootfs.tar.gz root.x86_64/ --strip-components=1" +
                 " --numeric-owner")
            os.chdir(temp_path)
        case "fedora":
            print("Extracting fedora rootfs to temporary location")
            Path("/tmp/eupnea-build/fedora-temp").mkdir()
            bash("tar xfp /tmp/eupnea-build/rootfs/fedora-rootfs.tar.xz -C /tmp/eupnea-build/rootfs/fedora-temp")
            with os.scandir("/tmp/eupnea-build/rootfs/fedora-temp") as scan:
                for entry in scan:
                    if entry.is_dir():
                        temp_rootfs_path = entry.path
                        break
            print("Copying fedora rootfs to /mnt/eupnea")
            bash("tar xvpf " + temp_rootfs_path + "/layer.tar -C /mnt/eupnea")


# Configure distro agnostic options
def post_extract(username: str, password: str, hostname: str, rebind_search: bool, distro, de_name) -> None:
    print("\n\033[96m" + "Configuring Eupnea" + "\033[0m")
    print("Copying resolv.conf")
    bash("cp --remove-destination /etc/resolv.conf /mnt/eupnea/etc/resolv.conf")
    # TODO: perhaps its not a good idea to cp firmware from host
    print("Copying firmare from host")
    Path("/mnt/eupnea/lib/firmware").mkdir(parents=True, exist_ok=True)
    bash("cp -r /lib/firmware/* /mnt/eupnea/lib/firmware/")
    print("Extracting kernel modules")
    rmdir("/mnt/eupnea/lib/modules", ignore_errors=True)
    Path("/mnt/eupnea/lib/modules").mkdir(parents=True, exist_ok=True)
    bash("tar xpf /tmp/eupnea-build/modules.tar.xz -C /mnt/eupnea/")  # the tar contains /lib/modules already
    if not (distro == "ubuntu" and de_name == "gnome"):  # Ubuntu + gnome has first time setup
        print("Configuring user")
        chroot('useradd --create-home --comment "" ' + username)
        chroot('echo "' + username + ':' + password + '" | chpasswd')
        match distro:
            case "ubuntu" | "debian":
                chroot("usermod -aG sudo " + username)
            case "arch" | "fedora":
                chroot("usermod -aG wheel " + username)
    print("Setting hostname")
    with open("/mnt/eupnea/etc/hostname", "w") as hostname_file:
        hostname_file.write(hostname)
    print("Copying eupnea utils")
    # TODO: add py utils when rewrite is finished
    bash("cp eupnea-scripts/scripts/* /mnt/eupnea/usr/local/bin/")
    chroot("chmod 755 /mnt/eupnea/usr/local/bin/*")
    print("Backing up default keymap and setting Chromebook layout")
    chroot("cp /mnt/eupnea/usr/share/X11/xkb/symbols/pc /mnt/eupnea/usr/share/X11/xkb/symbols/pc.default")
    chroot("cp -f configs/xkb/xkb.chromebook /mnt/eupnea/usr/share/X11/xkb/symbols/pc")
    if rebind_search:
        print("Rebinding search key to Caps Lock")
        chroot("cp /mnt/eupnea/usr/share/X11/xkb/keycodes/evdev /mnt/eupnea/usr/share/X11/xkb/keycodes/evdev.default")
        chroot("cp configs/xkb/xkb.chromebook /mnt/eupnea/usr/share/X11/xkb/symbols/pc")
    print("Configuring sleep")
    # disable deep sleep and hibernation
    # TODO: Fix sleep?
    Path("/mnt/eupnea/etc/systemd/").mkdir(exist_ok=True)
    with open("/mnt/eupnea/etc/systemd/sleep.conf", "a") as file:
        file.write("SuspendState=freeze\nHibernateState=freeze")
    # open kernel-modules.txt and then append its contents to the rootfs file
    with open("configs/kernel-modules.txt", "r") as repo_file:
        with open("/mnt/eupnea/etc/modules", "a") as file:
            file.write(repo_file.read())


def chroot(command: str) -> str:
    return sp.run('chroot /mnt/eupnea /bin/sh -c "' + command + '"', shell=True, capture_output=True).stdout.decode(
        "utf-8").strip()


if __name__ == "__main__":
    # Elevate script to root
    if os.geteuid() != 0:
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *args)
    args = process_args()
    if args.dev_build:
        print("\033[93m" + "Using dev kernel" + "\033[0m")
    user_input = user_input.user_input()
    prepare_host(user_input[0])
    if args.local_path is None:
        download_kernel(args.dev_build)
    else:
        if not args.local_path.endswith("/"):
            kernel_path = args.local_path + "/"
        else:
            kernel_path = args.local_path
        print("\033[96m" + "Using local kernel files" + "\033[0m")
        bash("cp " + kernel_path + "bzImage /tmp/eupnea-build/bzImage")
        bash("cp " + kernel_path + "modules.tar.xz /tmp/eupnea-build/modules.tar.xz")
    if user_input[9]:
        img_mnt = prepare_img()
    else:
        prepare_usb()
    download_rootfs(user_input[0], user_input[1], user_input[2])
    extract_rootfs(user_input[0])
    post_extract(user_input[5], user_input[6], user_input[7], user_input[8], user_input[0], user_input[3])
    match user_input[0]:
        case "ubuntu":
            import distro.ubuntu as distro
        case "debian":
            import distro.debian as distro
        case "arch":
            import distro.arch as distro
        case "fedora":
            import distro.fedora as distro
        case _:
            print("\033[91m" + "Something went **really** wrong somewhere!(Distro name not found)" + "\033[0m")
    distro.config(user_input[3], user_input[1])
    print("\033[96m" + "Finishing setup" + "\033[0m")
    print("Unmounting rootfs")
    bash("umount /mnt/eupnea")
    if user_input[9]:
        print("Unmounting img")
        bash("losetup -d " + img_mnt)
        print("\033[95m" + "The ready Eupnea image is located at " + str(os.getcwd()) + "/eupnea.img" + "\033[0m")
    else:
        print("\033[95m" + "The USB is ready to boot Eupnea. " + "\033[0m")
