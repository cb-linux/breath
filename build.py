#!/usr/bin/env python3

from typing import Tuple
from urllib.request import urlretrieve
from urllib.error import URLError
import json

from functions import *


# Clean /tmp from eupnea files
def prepare_host(de_name: str, user_id: str) -> None:
    print_status("Preparing host system")

    try:
        bash("umount -lf /tmp/eupnea-build/fedora-tmp-mnt 2>/dev/null")  # umount fedora temp if exists
    except subprocess.CalledProcessError:
        print("Failed to unmount /tmp/eupnea-build/fedora-tmp-mnt, ignore")
        pass

    print_status("Cleaning + preparing host system")
    rmdir("/tmp/eupnea-build")
    mkdir("/tmp/eupnea-build", create_parents=True)

    print_status("Creating mount points")
    try:
        bash("umount -lf /mnt/eupnea 2>/dev/null")  # just in case
    except subprocess.CalledProcessError:
        print("Failed to unmount /mnt/eupnea, ignore")
        pass
    rmdir("/mnt/eupnea")
    mkdir("/mnt/eupnea", True)

    rmfile("eupnea.img")
    rmfile("kernel.flags")

    install_vboot(user_id)

    # install debootstrap for debian
    if de_name == "debian" and not path_exists("/usr/sbin/debootstrap"):
        print_status("Installing debootstrap")
        if path_exists("/usr/bin/apt"):
            bash("apt-get install debootstrap -y")
        elif path_exists("/usr/bin/pacman"):
            bash("pacman -S debootstrap --noconfirm")
        elif path_exists("/usr/bin/dnf"):
            bash("dnf install debootstrap --assumeyes")
        elif path_exists("/usr/bin/zypper"):  # openSUSE
            bash("zypper --non-interactive install debootstrap")
        else:
            print_warning("Debootstrap not found, please install it using your disotros package manager or select "
                          "another distro instead of debian")
            exit(1)

    # install arch-chroot for arch
    if de_name == "arch" and not path_exists("/usr/bin/arch-chroot"):
        print_status("Installing arch-chroot")
        if path_exists("/usr/bin/apt"):
            bash("apt-get install arch-install-scripts -y")
        elif path_exists("/usr/bin/pacman"):
            bash("pacman -S arch-install-scripts --noconfirm")
        elif path_exists("/usr/bin/dnf"):
            bash("dnf install arch-install-scripts --assumeyes")
        elif path_exists("/usr/bin/zypper"):  # openSUSE
            bash("zypper --non-interactive install arch-install-scripts")
        else:
            print_warning("Arch-install-scripts not found, please install it using your distros package manager or "
                          "select another distro instead of arch")
            exit(1)


# download kernel files from GitHub
def download_kernel(kernel_type: str, dev_release: bool, main_pid: int) -> None:
    # select correct link
    if dev_release:
        url = "https://github.com/eupnea-linux/kernel/releases/download/dev-build/"
    else:
        url = "https://github.com/eupnea-linux/kernel/releases/latest/download/"

    # download kernel files
    start_progress()  # show fake progress
    try:
        match kernel_type:
            case "mainline":
                print_status("Downloading mainline kernel")
                url = "https://github.com/eupnea-linux/mainline-kernel/releases/latest/download/"
                urlretrieve(f"{url}bzImage-stable", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules-stable.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
                urlretrieve(f"{url}headers-stable.tar.xz", filename="/tmp/eupnea-build/headers.tar.xz")
            case "alt":
                print_status("Downloading alt kernel")
                urlretrieve(f"{url}bzImage-alt", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules-alt.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
            case "exp":
                print_status("Downloading experimental 5.15 kernel")
                urlretrieve(f"{url}bzImage-exp", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules-exp.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
            case "stable":
                print_status("Downloading stable 5.10 kernel")
                urlretrieve(f"{url}bzImage", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
    except URLError:
        print_error("Failed to reach github. Check your internet connection and try again or use local files with -l")
        bash(f"kill {main_pid}")  # stop whole script

    stop_progress()  # stop fake progress
    print_status("Kernel files downloaded successfully")


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
    try:
        match distro_name:
            case "ubuntu":
                print_status(f"Downloading ubuntu rootfs {distro_version}")
                start_progress(force_show=True)  # start fake progress
                urlretrieve(
                    f"https://cloud-images.ubuntu.com/releases/{distro_version}/release/ubuntu-{distro_version}"
                    f"-server-cloudimg-amd64-root.tar.xz",
                    filename="/tmp/eupnea-build/ubuntu-rootfs.tar.xz")
                stop_progress(force_show=True)
            case "debian":
                print_status("Creating debian with debootstrap")
                start_progress()  # start fake progress
                # Debian is debootstrapped directly to the device
                debian_result = bash(
                    "debootstrap stable /mnt/eupnea https://deb.debian.org/debian/")
                stop_progress()  # stop fake progress
                if debian_result.__contains__("Couldn't download packages:"):
                    print_error("Debootstrap failed, check your internet connection or try again later")
                    bash(f"kill {main_pid}")
            case "arch":
                print_status("Downloading latest arch rootfs")
                start_progress(force_show=True)  # start fake progress
                urlretrieve(distro_link, filename="/tmp/eupnea-build/arch-rootfs.tar.gz")
                stop_progress(force_show=True)  # stop fake progress
            case "fedora":
                print_status(f"Downloading fedora rootfs version: {distro_version}")
                start_progress(force_show=True)  # start fake progress
                urlretrieve(distro_link, filename="/tmp/eupnea-build/fedora-rootfs.raw.xz")
                stop_progress(force_show=True)  # stop fake progress
    except URLError:
        print_error("Couldn't download rootfs. Check your internet connection and try again. If the error persists, "
                    "create an issue with the distro and version in the name")
        bash(f"kill {main_pid}")  # stop whole script


# Download firmware for later
def download_firmware(main_pid: int) -> None:
    print_status("Downloading firmware")
    start_progress()  # start fake progress
    try:
        bash("git clone --depth=1 https://chromium.googlesource.com/chromiumos/third_party/linux-firmware/ "
             "/tmp/eupnea-build/firmware")
    except URLError:
        print("\033[91m" + "Couldn't download firmware. Check your internet connection and try again." + "\033[0m")
        bash(f"kill {main_pid}")
    stop_progress()  # stop fake progress


# extract the rootfs to /mnt/eupnea
def extract_rootfs(distro_name: str) -> None:
    print_status("Extracting rootfs")
    match distro_name:
        case "ubuntu":
            print_status("Extracting ubuntu rootfs")
            # --checkpoint is for printing real tar progress
            bash("tar xfp /tmp/eupnea-build/ubuntu-rootfs.tar.xz -C /mnt/eupnea --checkpoint=.10000")
        case "debian":
            # Debian gets debootstrapped directly to the device, no need to copy
            print_status("Copying debian was debootstrapped, skipping")
        case "arch":
            print_status("Extracting arch rootfs")
            mkdir("/tmp/eupnea-build/arch-rootfs")
            bash("tar xfp /tmp/eupnea-build/arch-rootfs.tar.gz -C /tmp/eupnea-build/arch-rootfs --checkpoint=.10000")
            start_progress()  # start fake progress
            cpdir("/tmp/eupnea-build/arch-rootfs/root.x86_64/", "/mnt/eupnea/")
            stop_progress()  # stop fake progress
        case "fedora":
            print_status("Extracting fedora rootfs")
            # extract raw image to temp location
            mkdir("/tmp/eupnea-build/fedora-tmp-mnt")
            # using unxz instead of tar
            bash("unxz -d /tmp/eupnea-build/fedora-rootfs.raw.xz -c > /tmp/eupnea-build/fedora-raw")

            # mount fedora raw image as loop device
            fedora_root_part = bash("losetup -P -f --show /tmp/eupnea-build/fedora-raw") + "p5"  # part 5 is the rootfs
            bash(f"mount {fedora_root_part} /tmp/eupnea-build/fedora-tmp-mnt")  # mount 5th root partition as filesystem
            print_status("Copying fedora rootfs to /mnt/eupnea")
            cpdir("/tmp/eupnea-build/fedora-tmp-mnt/root/", "/mnt/eupnea/")  # copy mounted rootfs to /mnt/eupnea

            # unmount fedora image to prevent errors and unused loop devices
            bash(f"umount -fl /tmp/eupnea-build/fedora-tmp-mnt")
            bash(f"losetup -d {fedora_root_part[:-2]}")
    print_status("\n" + "Rootfs extraction complete")


# Configure distro agnostic options
def post_extract(username: str, password: str, hostname: str, distro_name: str, de_name: str, kernel_type: str) -> None:
    print_status("Applying distro agnostic configuration")

    # Extract kernel modules
    rmdir("/mnt/eupnea/lib/modules/")  # delete old modules, if present
    # modules.tar.xz contains /lib/modules, so it's extracted to / and --skip-old-files is used to prevent it from
    # overwriting other files in /lib
    bash("tar xpf /tmp/eupnea-build/modules.tar.xz --skip-old-files -C /mnt/eupnea/ --checkpoint=.10000")
    print("")  # break line after tar

    # Extract kernel headers
    print_status("Extracting kernel headers")
    # TODO: extract kernel headers

    # Copy resolv.conf from host to eupnea
    rmfile("/mnt/eupnea/etc/resolv.conf", True)  # delete broken symlink
    cpfile("/etc/resolv.conf", "/mnt/eupnea/etc/resolv.conf")

    # Set device hostname
    with open("/mnt/eupnea/etc/hostname", "w") as hostname_file:
        hostname_file.write(hostname)

    # Copy eupnea scripts and config
    cpdir("postinstall-scripts", "/mnt/eupnea/usr/local/bin/")
    chroot("chmod 755 /usr/local/bin/*")  # make scripts executable in system
    cpfile("functions.py", "/mnt/eupnea/usr/local/bin/functions.py")  # copy functions file
    # copy configs
    mkdir("/mnt/eupnea/usr/local/eupnea-configs")
    cpdir("configs", "/mnt/eupnea/usr/local/eupnea-configs")

    # create eupnea settings file for future needs
    with open("configs/eupnea-settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    settings["kernel_type"] = kernel_type
    with open("/mnt/eupnea/usr/local/eupnea-settings.json", "w") as settings_file:
        json.dump(settings, settings_file)

    # disable hibernation aka S4 sleep, READ: https://eupnea-linux.github.io/docs.html#/bootlock
    # TODO: Fix sleep, maybe
    mkdir("/mnt/eupnea/etc/systemd/")  # just in case systemd path doesn't exist
    with open("/mnt/eupnea/etc/systemd/sleep.conf", "a") as conf:
        conf.write("SuspendState=freeze\nHibernateState=freeze")

    # Enable loading modules needed for eupnea
    cpfile("configs/eupnea-modules.conf", "/mnt/eupnea/etc/modules-load.d/eupnea-modules.conf")

    # TODO: Fix failing services
    # The services below fail to start, so they are disabled

    # ssh
    rmfile("/mnt/eupnea/etc/systemd/system/multi-user.target.wants/ssh.service")
    rmfile("/mnt/eupnea/etc/systemd/system/sshd.service")

    # Add user to system if the DE has no first time setup
    if not (distro_name == "ubuntu" and de_name == "gnome"):  # Ubuntu + gnome has a first time setup
        print_status("Configuring user")
        chroot(f"useradd --create-home --shell /bin/bash {username}")
        # TODO: Fix ) and ( crashing chpasswd
        chroot(f'echo "{username}:{password}" | chpasswd')
        match distro_name:
            case "ubuntu" | "debian":
                chroot(f"usermod -aG sudo {username}")
            case "arch" | "fedora":
                chroot(f"usermod -aG wheel {username}")


# post extract and distro config
def post_config(rebind_search: bool) -> None:
    # Add chromebook layout. Needs to be done after install Xorg
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
    start_progress(force_show=True)  # start fake progress
    cpdir("/tmp/eupnea-build/firmware", "/mnt/eupnea/lib/firmware")
    stop_progress(force_show=True)  # stop fake progress


# chroot command
def chroot(command: str) -> str:
    return bash(f'chroot /mnt/eupnea /bin/sh -c "{command}"')


# The main build script
def start_build(verbose: bool, local_path: str, kernel_type: str, dev_release: bool, main_pid: int, user_id: str,
                build_options):
    set_verbose(verbose)

    # Most errors happen in the preparation. To avoid unnecessary downloads the storage device is prepared before
    # downloading files
    prepare_host(build_options["distro_name"], user_id)
    if build_options["device"] == "image":
        output_temp = prepare_img()
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]
    else:
        output_temp = prepare_usb(build_options["device"])
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]

    if local_path is None:
        download_kernel(kernel_type, dev_release, main_pid)
        download_rootfs(build_options["distro_name"], build_options["distro_version"], build_options["distro_link"],
                        main_pid)
        download_firmware(main_pid)
    else:  # if local path is specified, copy files from it, instead of downloading from the internet
        # clean local path string
        if not local_path.endswith("/"):
            local_path_posix = f"{local_path}/"
        else:
            local_path_posix = local_path

        print_status("Copying local files to tmp")
        try:
            cpfile(f"{local_path_posix}bzImage", "/tmp/eupnea-build/bzImage")
            cpfile(f"{local_path_posix}modules.tar.xz", "/tmp/eupnea-build/modules.tar.xz")
            cpdir(f"{local_path_posix}firmware", "/mnt/eupnea/lib/firmware/google")
            match build_options["distro_name"]:
                case "ubuntu":
                    cpfile(f"{local_path_posix}ubuntu-rootfs.tar.xz", "/tmp/eupnea-build/ubuntu-rootfs.tar.xz")
                case "debian":
                    cpdir(f"{local_path_posix}debian", "/tmp/eupnea-build/debian")
                case "arch":
                    cpfile(f"{local_path_posix}arch-rootfs.tar.gz", "/tmp/eupnea-build/arch-rootfs.tar.gz")
                case "fedora":
                    cpfile(f"{local_path_posix}fedora-rootfs.raw.xz", "/tmp/eupnea-build/fedora-rootfs.raw.xz")
                case _:
                    print_error("Distro name not found, please create an issue")
                    exit(1)
        except FileNotFoundError:
            print_error("Local rootfs not found, please verify the file name is correct")
            exit(1)

    extract_rootfs(build_options["distro_name"])
    post_extract(build_options["username"], build_options["password"], build_options["hostname"],
                 build_options["distro_name"], build_options["de_name"], kernel_type)

    match build_options["distro_name"]:
        case "ubuntu":
            import distro.ubuntu as distro
        case "debian":
            import distro.debian as distro
        case "arch":
            import distro.arch as distro
        case "fedora":
            import distro.fedora as distro
        case _:
            # Just in case
            print_error("DISTRO NAME NOT FOUND! Please create an issue")
            exit(1)
    distro.config(build_options["de_name"], build_options["distro_version"], root_partuuid, verbose)

    post_config(build_options["rebind_search"])

    # Post-install cleanupp
    print_status("Cleaning up host system after build")
    bash("umount -f /mnt/eupnea")
    if build_options["device"] == "image":
        bash(f"losetup -d {img_mnt}")
        print_header(f"The ready-to-boot Eupnea image is located at {get_full_path('.')}/eupnea.img")
    else:
        print_header("It is safe to remove the USB-drive/SD-card now.")
    print_header("Thank you for using Eupnea!")


if __name__ == "__main__":
    print_error("Do not run this file directly. Instead, run main.py")
