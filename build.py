#!/usr/bin/env python3

from typing import Tuple
from urllib.request import urlretrieve
from urllib.error import URLError
import json

from functions import *


# Clean /tmp from eupnea files
def prepare_host(de_name: str) -> None:
    print_status("Preparing host system")

    # unmount fedora remains before attempting to remove /tmp/eupnea-build
    try:
        bash("umount -lf /tmp/eupnea-build/fedora-tmp-mnt 2>/dev/null")  # umount fedora temp if exists
    except subprocess.CalledProcessError:
        print("Failed to unmount /tmp/eupnea-build/fedora-tmp-mnt, ignore")
        pass

    # unmount cdrom remains before attempting to remove /tmp/eupnea-build
    try:
        bash("umount -lf /tmp/eupnea-build/cdrom 2>/dev/null")  # umount fedora temp if exists
    except subprocess.CalledProcessError:
        print("Failed to unmount /tmp/eupnea-build/cdrom, ignore")
        pass

    print_status("Cleaning + preparing host system")
    rmdir("/tmp/eupnea-build")
    mkdir("/tmp/eupnea-build", create_parents=True)

    print_status("Creating mount points")
    try:
        bash("umount -lf /mnt/eupnea")  # just in case
        sleep(1)  # wait for umount to finish
    except subprocess.CalledProcessError:
        print("Failed to unmount /mnt/eupnea, ignore")
        pass
    rmdir("/mnt/eupnea")
    mkdir("/mnt/eupnea", create_parents=True)

    rmfile("eupnea.img")
    rmfile("kernel.flags")

    # Install dependencies
    install_kernel_packages()
    # Install parted
    if not path_exists("/usr/sbin/parted"):
        print_status("Installing parted")
        if path_exists("/usr/bin/apt"):  # Ubuntu + debian
            bash("apt-get install parted -y")
        elif path_exists("/usr/bin/pacman"):  # Arch
            bash("pacman -S parted --noconfirm")
        elif path_exists("/usr/bin/dnf"):  # Fedora
            bash("dnf install parted --assumeyes")
        elif path_exists("/usr/bin/zypper"):  # openSUSE
            bash("zypper --non-interactive install parted")
        else:
            print_warning("Parted not found, please install it using your distros package manager")
            exit(1)

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
            print_warning("Debootstrap not found, please install it using your distros package manager or select "
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

    # install unsquashfs for pop-os
    if de_name == "pop-os" and not path_exists("/usr/bin/unsquashfs"):
        print_status("Installing unsquashfs")
        if path_exists("/usr/bin/apt"):
            bash("apt-get install squashfs-tools -y")
        elif path_exists("/usr/bin/pacman"):
            bash("pacman -S squashfs-tools --noconfirm")
        elif path_exists("/usr/bin/dnf"):
            bash("dnf install squashfs-tools --assumeyes")
        elif path_exists("/usr/bin/zypper"):  # openSUSE
            bash("zypper --non-interactive install squashfs-tools")
        else:
            print_warning("'squashfs-tools' not found, please install it using your distros package manager or select "
                          "another distro instead of Pop!_OS")
            exit(1)

        # download kernel files from GitHub


def download_kernel(kernel_type: str, dev_release: bool) -> None:
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
                urlretrieve(f"{url}headers-alt.tar.xz", filename="/tmp/eupnea-build/headers.tar.xz")
            case "exp":
                print_status("Downloading experimental 5.15 kernel")
                urlretrieve(f"{url}bzImage-exp", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules-exp.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
                urlretrieve(f"{url}headers-exp.tar.xz", filename="/tmp/eupnea-build/headers.tar.xz")
            case "stable":
                print_status("Downloading stable 5.10 kernel")
                urlretrieve(f"{url}bzImage", filename="/tmp/eupnea-build/bzImage")
                urlretrieve(f"{url}modules.tar.xz", filename="/tmp/eupnea-build/modules.tar.xz")
                urlretrieve(f"{url}headers.tar.xz", filename="/tmp/eupnea-build/headers.tar.xz")
    except URLError:
        print_error("Failed to reach github. Check your internet connection and try again or use local files with -l")
        exit(1)

    stop_progress()  # stop fake progress
    print_status("Kernel files downloaded successfully")


# download the distro rootfs
def download_rootfs(distro_name: str, distro_version: str, distro_link: str) -> None:
    try:
        match distro_name:
            case "ubuntu":
                print_status(f"Downloading ubuntu rootfs {distro_version}")
                start_download_progress("/tmp/eupnea-build/ubuntu-rootfs.tar.xz")
                urlretrieve(
                    f"https://cloud-images.ubuntu.com/releases/{distro_version}/release/ubuntu-{distro_version}"
                    f"-server-cloudimg-amd64-root.tar.xz",
                    filename="/tmp/eupnea-build/ubuntu-rootfs.tar.xz")
                stop_download_progress()
            case "debian":
                print_status("Debian is downloaded later, skipping download")
            case "arch":
                print_status("Downloading latest arch rootfs")
                start_download_progress("/tmp/eupnea-build/arch-rootfs.tar.gz")
                urlretrieve(distro_link, filename="/tmp/eupnea-build/arch-rootfs.tar.gz")
                stop_download_progress()
            case "fedora":
                print_status(f"Downloading fedora rootfs version: {distro_version}")
                start_download_progress("/tmp/eupnea-build/fedora-rootfs.raw.xz")
                urlretrieve(distro_link, filename="/tmp/eupnea-build/fedora-rootfs.raw.xz")
                stop_download_progress()
            case "pop-os":
                print_status(f"Downloading Pop!_OS iso {distro_version}")
                start_download_progress("/tmp/eupnea-build/pop-os.iso")
                urlretrieve(
                    "https://iso.pop-os.org/22.04/amd64/intel/14/pop-os_22.04_amd64_intel_14.iso",
                    filename="/tmp/eupnea-build/pop-os.iso")
                stop_download_progress()
    except URLError:
        print_error("Couldn't download rootfs. Check your internet connection and try again. If the error persists, "
                    "create an issue with the distro and version in the name")
        exit(1)


# Download firmware for later
def download_firmware() -> None:
    print_status("Downloading firmware")
    start_progress()  # start fake progress
    try:
        bash("git clone --depth=1 https://chromium.googlesource.com/chromiumos/third_party/linux-firmware/ "
             "/tmp/eupnea-build/firmware")
    except URLError:
        print_error("Couldn't download firmware. Check your internet connection and try again.")
        exit(1)
    stop_progress()  # stop fake progress


# Download postinstall scripts
def download_postinstall_scripts() -> None:
    print_status("Downloading postinstall scripts")
    start_progress()  # start fake progress
    try:
        bash("git clone --depth=1 https://github.com/eupnea-linux/postinstall-scripts "
             "/tmp/eupnea-build/postinstall-scripts")
    except URLError:
        print_error("Couldn't download postinstall scripts. Check your internet connection and try again.")
        exit(1)
    stop_progress()  # stop fake progress


# Download postinstall scripts
def download_audio_scripts() -> None:
    print_status("Downloading audio scripts")
    start_progress()  # start fake progress
    try:
        bash("git clone --depth=1 https://github.com/eupnea-linux/audio-scripts "
             "/tmp/eupnea-build/audio-scripts")
    except URLError:
        print_error("Couldn't download audio scripts. Check your internet connection and try again.")
        exit(1)
    stop_progress()  # stop fake progress


# Create, mount, partition the img and flash the eupnea kernel
def prepare_img(distro_name: str) -> Tuple[str, str]:
    print_status("Preparing image")

    # TODO: dynamic img size
    img_size = 10
    try:
        bash(f"fallocate -l {img_size}G eupnea.img")
    except subprocess.CalledProcessError:  # try fallocate, if it fails use dd
        bash("dd if=/dev/zero of=eupnea.img status=progress bs=12884 count=1000070")

    print_status("Mounting empty image")
    mnt_point = bash("losetup -f --show eupnea.img")
    if mnt_point == "":
        print_error("Failed to mount image")
        exit(1)
    return partition_and_flash_kernel(mnt_point, False, distro_name)


# Prepare USB, usb is not yet fully implemented
def prepare_usb(device: str, distro_name: str) -> Tuple[str, str]:
    print_status("Preparing USB")

    # fix device name if needed
    if device.endswith("/") or device.endswith("1") or device.endswith("2"):
        device = device[:-1]
    # add /dev/ to device name, if needed
    if not device.startswith("/dev/"):
        device = f"/dev/{device}"

    # unmount all partitions
    try:
        bash(f"umount -lf {device}*")
    except subprocess.CalledProcessError:
        pass
    return partition_and_flash_kernel(device, True, distro_name)


def partition_and_flash_kernel(mnt_point: str, write_usb: bool, distro_name: str) -> Tuple[str, str]:
    print_status("Preparing device/image partition")

    # Determine rootfs part name
    if write_usb:
        # if writing to usb, then no p in partition name
        rootfs_mnt = mnt_point + "2"
    else:
        # image is a loop device -> needs p in part name
        rootfs_mnt = mnt_point + "p2"

    # remove pre-existing partition table from usb
    if write_usb:
        bash(f"wipefs -af {mnt_point}")

    # format as per depthcharge requirements,
    # READ: https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices
    bash(f"parted -s {mnt_point} mklabel gpt")
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Kernel 1 65")  # kernel partition
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Root 65 100%")  # rootfs partition
    bash(f"cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 {mnt_point}")  # depthcharge flags

    # get uuid of rootfs partition
    rootfs_partuuid = bash(f"blkid -o value -s PARTUUID {rootfs_mnt}")

    # write PARTUUID to kernel flags and save it as a file
    with open(f"configs/cmdlines/{distro_name}.flags", "r") as flags:
        temp_cmdline = flags.read().replace("${USB_ROOTFS}", rootfs_partuuid).strip()
    with open("kernel.flags", "w") as config:
        config.write(temp_cmdline)

    print_status("Flashing kernel to device/image")
    # Sign kernel
    bash("futility vbutil_kernel --arch x86_64 --version 1 --keyblock /usr/share/vboot/devkeys/kernel.keyblock"
         + " --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk --bootloader kernel.flags" +
         " --config kernel.flags --vmlinuz /tmp/eupnea-build/bzImage --pack /tmp/eupnea-build/bzImage.signed")

    # Flash kernel
    if write_usb:
        # if writing to usb, then no p in partition name
        bash(f"dd if=/tmp/eupnea-build/bzImage.signed of={mnt_point}1")
    else:
        # image is a loop device -> needs p in part name
        bash(f"dd if=/tmp/eupnea-build/bzImage.signed of={mnt_point}p1")

    print_status("Formatting rootfs part")
    # Create rootfs ext4 partition
    bash(f"yes 2>/dev/null | mkfs.ext4 {rootfs_mnt}")  # 2>/dev/null is to supress yes broken pipe warning

    # Mount rootfs partition
    bash(f"mount {rootfs_mnt} /mnt/eupnea")

    print_status("Device/image preparation complete")
    return mnt_point, rootfs_partuuid  # return loop device, so it can be unmounted at the end


# extract the rootfs to /mnt/eupnea
def extract_rootfs(distro_name: str) -> None:
    print_status("Extracting rootfs")
    match distro_name:
        case "ubuntu":
            print_status("Extracting ubuntu rootfs")
            # --checkpoint is for printing real tar progress
            bash("tar xfp /tmp/eupnea-build/ubuntu-rootfs.tar.xz -C /mnt/eupnea --checkpoint=.10000")
        case "debian":
            print_status("Debootstraping into /mnt/eupnea")
            start_progress()  # start fake progress
            # debootstrapping directly to /mnt/eupnea
            debian_result = bash(
                "debootstrap stable /mnt/eupnea https://deb.debian.org/debian/")
            stop_progress()  # stop fake progress
            if debian_result.__contains__("Couldn't download packages:"):
                print_error("Debootstrap failed, check your internet connection or try again later")
                exit(1)
        case "arch":
            print_status("Extracting arch rootfs")
            mkdir("/tmp/eupnea-build/arch-rootfs")
            bash("tar xfp /tmp/eupnea-build/arch-rootfs.tar.gz -C /tmp/eupnea-build/arch-rootfs --checkpoint=.10000")
            start_progress(force_show=True)  # start fake progress
            cpdir("/tmp/eupnea-build/arch-rootfs/root.x86_64/", "/mnt/eupnea/")
            stop_progress(force_show=True)  # stop fake progress
        case "fedora":
            print_status("Extracting fedora rootfs")
            # extract raw image to temp location
            mkdir("/tmp/eupnea-build/fedora-tmp-mnt")
            # using unxz instead of tar
            bash("unxz -d /tmp/eupnea-build/fedora-rootfs.raw.xz -c > /tmp/eupnea-build/fedora-raw")

            bash("modprobe btrfs")  # some systems don't have btrfs module loaded by default.

            # mount fedora raw image as loop device
            fedora_root_part = bash("losetup -P -f --show /tmp/eupnea-build/fedora-raw") + "p5"  # part 5 is the rootfs
            bash(f"mount {fedora_root_part} /tmp/eupnea-build/fedora-tmp-mnt")  # mount 5th root partition as filesystem
            print_status("Copying fedora rootfs to /mnt/eupnea")
            cpdir("/tmp/eupnea-build/fedora-tmp-mnt/root/", "/mnt/eupnea/")  # copy mounted rootfs to /mnt/eupnea

            # unmount fedora image to prevent errors and unused loop devices
            try:
                bash(f"umount -fl /tmp/eupnea-build/fedora-tmp-mnt")
            except subprocess.CalledProcessError:  # fails on Crostini
                pass
            bash(f"losetup -d {fedora_root_part[:-2]}")
        case "pop-os":
            print_status("Extracting Pop!_OS squashfs from iso")
            # Create a mount point for the iso to extract the squashfs
            mkdir("/tmp/eupnea-build/iso")
            mnt_iso = bash(f"losetup -f --show /tmp/eupnea-build/pop-os.iso")
            mkdir("/tmp/eupnea-build/cdrom")
            bash(f"mount {mnt_iso} /tmp/eupnea-build/cdrom")
            bash("unsquashfs -f -d /mnt/eupnea /tmp/eupnea-build/cdrom/casper/filesystem.squashfs")
            try:
                bash("umount -fl /tmp/eupnea-build/cdrom")  # pop-os loop device
                bash(f"losetup -d {mnt_iso} ")
            except subprocess.CalledProcessError:
                pass  # on crostini umount fails for some reason

    print_status("\n" + "Rootfs extraction complete")


# Configure distro agnostic options
def post_extract(build_options, kernel_type: str) -> None:
    print_status("Applying distro agnostic configuration")

    # Extract modules
    print_status("Extracting kernel modules")
    rmdir("/mnt/eupnea/lib/modules")  # remove all old modules
    mkdir("/mnt/eupnea/lib/modules")
    bash(f"tar xpf /tmp/eupnea-build/modules.tar.xz -C /mnt/eupnea/lib/modules/ --checkpoint=.10000")
    print("")  # break line after tar

    # Extract kernel headers
    print_status("Extracting kernel headers")
    dir_kernel_version = bash(f"ls /mnt/eupnea/lib/modules/").strip()  # get modules dir name
    rmdir(f"/mnt/eupnea/usr/src/linux-headers-{dir_kernel_version}", keep_dir=False)  # remove old headers
    mkdir(f"/mnt/eupnea/usr/src/linux-headers-{dir_kernel_version}", create_parents=True)
    bash(f"tar xpf /tmp/eupnea-build/headers.tar.xz -C /mnt/eupnea/usr/src/linux-headers-{dir_kernel_version}/ "
         f"--checkpoint=.10000")
    print("")  # break line after tar
    chroot(f"ln -s /usr/src/linux-headers-{dir_kernel_version}/ "
           f"/lib/modules/{dir_kernel_version}/build")  # use chroot for correct symlink

    # Copy resolv.conf from host to eupnea
    rmfile("/mnt/eupnea/etc/resolv.conf", True)  # delete broken symlink
    cpfile("/etc/resolv.conf", "/mnt/eupnea/etc/resolv.conf")

    # Set device hostname
    with open("/mnt/eupnea/etc/hostname", "w") as hostname_file:
        hostname_file.write(build_options["hostname"] + "\n")

    # Copy eupnea scripts and config
    print_status("Copying eupnea scripts and configs")
    # Copy postinstall scripts
    for file in Path("/tmp/eupnea-build/postinstall-scripts").iterdir():
        if file.is_file():
            if file.name == "LICENSE" or file.name == "README.md" or file.name == ".gitignore":
                continue  # dont copy license, readme and gitignore
            else:
                cpfile(file.absolute().as_posix(), f"/mnt/eupnea/usr/local/bin/{file.name}")
    # copy audio setup script
    cpfile("/tmp/eupnea-build/audio-scripts/setup-audio", "/mnt/eupnea/usr/local/bin/setup-audio")
    # copy functions file
    cpfile("functions.py", "/mnt/eupnea/usr/local/bin/functions.py")
    chroot("chmod 755 /usr/local/bin/*")  # make scripts executable in system

    # copy configs
    mkdir("/mnt/eupnea/etc/eupnea")
    cpdir("configs", "/mnt/eupnea/etc/eupnea")  # eupnea-builder configs
    cpdir("/tmp/eupnea-build/postinstall-scripts/configs", "/mnt/eupnea/etc/eupnea")  # postinstall configs
    cpdir("/tmp/eupnea-build/audio-scripts/configs", "/mnt/eupnea/etc/eupnea")  # audio configs

    # create eupnea settings file for postinstall scripts to read
    with open("configs/eupnea.json", "r") as settings_file:
        settings = json.load(settings_file)
    settings["kernel_type"] = kernel_type
    # TODO: set kernel_version
    settings["distro_name"] = build_options["distro_name"]
    settings["de_name"] = build_options["de_name"]
    if not build_options["device"] == "image":
        settings["eupnea_install_type"] = "direct"
    with open("/mnt/eupnea/etc/eupnea.json", "w") as settings_file:
        json.dump(settings, settings_file)

    print_status("Fixing sleep")
    # disable hibernation aka S4 sleep, READ: https://eupnea-linux.github.io/docs.html#/pages/bootlock
    # TODO: Fix sleep, maybe
    mkdir("/mnt/eupnea/etc/systemd/")  # just in case systemd path doesn't exist
    with open("/mnt/eupnea/etc/systemd/sleep.conf", "a") as conf:
        conf.write("SuspendState=freeze\nHibernateState=freeze\n")

    # Enable loading modules needed for eupnea
    cpfile("configs/eupnea-modules.conf", "/mnt/eupnea/etc/modules-load.d/eupnea-modules.conf")

    # TODO: Fix failing services
    # The services below fail to start, so they are disabled

    # ssh
    rmfile("/mnt/eupnea/etc/systemd/system/multi-user.target.wants/ssh.service")
    rmfile("/mnt/eupnea/etc/systemd/system/sshd.service")

    username = build_options["username"]  # quotes interfere with functions below
    password = build_options["password"]  # quotes interfere with functions below

    # Do not pre-setup gnome, as there is a nice gui first time setup on first boot
    if not build_options["de_name"] == "gnome":
        print_status("Configuring user")
        chroot(f"useradd --create-home --shell /bin/bash {username}")
        # TODO: Fix ) and ( crashing chpasswd
        chroot(f'echo "{username}:{password}" | chpasswd')
        match build_options["distro_name"]:
            case "ubuntu" | "debian":
                chroot(f"usermod -aG sudo {username}")
            case "arch" | "fedora":
                chroot(f"usermod -aG wheel {username}")
            case "pop-os":
                sleep(5)  # need to sleep for some reasons
                chroot(f"usermod -aG adm,sudo,lpadmin {username}")

        # set timezone build system timezone on eupnea
        host_time_zone = bash("file /etc/localtime")  # read host timezone link
        host_time_zone = host_time_zone[host_time_zone.find("/usr/share/zoneinfo/"):].strip()  # get actual timezone
        chroot(f"ln -sf {host_time_zone} /etc/localtime")

    print_status("Distro agnostic configuration complete")


# post extract and distro config
def post_config(rebind_search: bool) -> None:
    # Add chromebook layout. Needs to be done after install Xorg
    print_status("Backing up default keymap and setting Chromebook layout")
    cpfile("/mnt/eupnea/usr/share/X11/xkb/symbols/pc", "/mnt/eupnea/usr/share/X11/xkb/symbols/pc.default")
    cpfile("configs/xkb/xkb.chromebook", "/mnt/eupnea/usr/share/X11/xkb/symbols/pc")
    if rebind_search:  # rebind search key to caps lock
        print("Rebinding search key to Caps Lock")
        cpfile("/mnt/eupnea/usr/share/X11/xkb/keycodes/evdev", "/mnt/eupnea/usr/share/X11/xkb/keycodes/evdev.default")

    # Add postinstall service
    print_status("Adding postinstall service")
    cpfile("configs/postinstall.service", "/mnt/eupnea/etc/systemd/system/postinstall.service")
    chroot("systemctl enable postinstall.service")

    # copy previously downloaded firmware
    print_status("Copying google firmware")
    rmdir("/mnt/eupnea/lib/firmware")
    start_progress(force_show=True)  # start fake progress
    cpdir("/tmp/eupnea-build/firmware", "/mnt/eupnea/lib/firmware")
    stop_progress(force_show=True)  # stop fake progress


# chroot command
def chroot(command: str) -> str:
    return bash(f'chroot /mnt/eupnea /bin/sh -c "{command}"')


# The main build script
def start_build(verbose: bool, local_path: str, kernel_type: str, dev_release: bool, build_options):
    set_verbose(verbose)
    print_status("Starting build")

    prepare_host(build_options["distro_name"])

    # Download files first
    if local_path is None:
        download_kernel(kernel_type, dev_release)
        download_rootfs(build_options["distro_name"], build_options["distro_version"], build_options["distro_link"])
        download_firmware()
        download_postinstall_scripts()
        download_audio_scripts()
    else:  # if local path is specified, copy files from it, instead of downloading from the internet
        # clean local path string
        if not local_path.endswith("/"):
            local_path_posix = f"{local_path}/"
        else:
            local_path_posix = local_path

        print_status("Copying local files to /tmp/eupnea-build")
        try:
            cpfile(f"{local_path_posix}bzImage", "/tmp/eupnea-build/bzImage")
            cpfile(f"{local_path_posix}modules.tar.xz", "/tmp/eupnea-build/modules.tar.xz")
            cpfile(f"{local_path_posix}headers.tar.xz", "/tmp/eupnea-update/headers.tar.xz")
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
                case "pop-os":
                    cpfile(f"{local_path_posix}pop-os.iso", "/tmp/eupnea-build/pop-os.iso")
                case _:
                    print_error("Distro name not found, please create an issue")
                    exit(1)
        except FileNotFoundError:
            print_error("A file could not be found. Verify all file names are correct (use --help to see correct names")
            exit(1)

    # Setup device
    if build_options["device"] == "image":
        output_temp = prepare_img(build_options["distro_name"])
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]
    else:
        output_temp = prepare_usb(build_options["device"], build_options["distro_name"])
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]

    # Extract rootfs and configure distro agnostic settings
    extract_rootfs(build_options["distro_name"])
    post_extract(build_options, kernel_type)

    match build_options["distro_name"]:
        case "ubuntu":
            import distro.ubuntu as distro
        case "debian":
            import distro.debian as distro
        case "arch":
            import distro.arch as distro
        case "fedora":
            import distro.fedora as distro
        case "pop-os":
            import distro.popos as distro
        case _:
            print_error("DISTRO NAME NOT FOUND! Please create an issue")
            exit(1)
    distro.config(build_options["de_name"], build_options["distro_version"], build_options["username"], root_partuuid,
                  verbose)

    post_config(build_options["rebind_search"])

    # Post-install cleanup
    print_status("Cleaning up host system after build")
    try:
        bash("umount -f /mnt/eupnea")
    except subprocess.CalledProcessError:  # on crostini umount fails for some reason
        pass
    if build_options["device"] == "image":
        bash(f"losetup -d {img_mnt}")
        print_header(f"The ready-to-boot Eupnea image is located at {get_full_path('.')}/eupnea.img")
    else:
        print_header("USB/SD-card is ready to boot Eupnea")
        print_header("It is safe to remove the USB-drive/SD-card now.")
    print_header("Thank you for using Eupnea!")


if __name__ == "__main__":
    print_error("Do not run this file directly. Instead, run main.py")
