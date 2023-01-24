#!/usr/bin/env python3

import contextlib
import atexit
import json
import sys
from typing import Tuple
from urllib.error import URLError

from functions import *

img_mnt = ""  # empty to avoid variable not defined error in exit_handler


def exit_handler():
    # Only trigger cleanup if the user initiated the exit, not if the script exited on its own
    exc_type = sys.exc_info()[0]
    if exc_type != KeyboardInterrupt:
        return
    print_error("Ctrl+C detected. Cleaning machine and exiting...")
    # Kill arch gpg agent if present
    print_status("Killing gpg-agent arch processes if they exist")
    gpg_pids = []
    for line in bash("ps aux").split("\n"):
        if "gpg-agent --homedir /etc/pacman.d/gnupg --use-standard-socket --daemon" in line:
            temp_string = line[line.find(" "):].strip()
            gpg_pids.append(temp_string[:temp_string.find(" ")])
    for pid in gpg_pids:
        print(f"Killing gpg-agent proces with pid: {pid}")
        bash(f"kill {pid}")

    print_status("Unmounting partitions")
    with contextlib.suppress(subprocess.CalledProcessError):
        bash("umount -lf /mnt/depthboot")  # umount mountpoint
    sleep(5)  # wait for umount to finish

    # unmount image/device completely from system
    # on crostini umount fails for some reason
    with contextlib.suppress(subprocess.CalledProcessError):
        bash(f"umount -lf {img_mnt}p*")  # umount all partitions from image
    with contextlib.suppress(subprocess.CalledProcessError):
        bash(f"umount -lf {img_mnt}*")  # umount all partitions from usb/sd-card


# Clean old depthboot files from /tmp
def prepare_host(de_name: str) -> None:
    print_status("Cleaning + preparing host system")
    # Clean system from previous depthboot builds
    rmdir("/tmp/depthboot-build")
    mkdir("/tmp/depthboot-build", create_parents=True)

    print_status("Creating mount points")
    try:
        bash("umount -lf /mnt/depthboot")  # just in case
        sleep(5)  # wait for umount to finish
        bash("umount -lf /mnt/depthboot")  # umount a second time, coz first time might not work
    except subprocess.CalledProcessError:
        print("Failed to unmount /mnt/depthboot, ignore")
    rmdir("/mnt/depthboot")
    mkdir("/mnt/depthboot", create_parents=True)

    rmfile("depthboot.img")
    rmfile("kernel.flags")
    rmfile(".stop_download_progress")

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


# download kernel files from GitHub
def download_kernel(kernel_type: str, dev_release: bool, files: list = None) -> str:
    if files is None:
        files = ["bzImage", "modules", "headers"]
    # select correct link
    if dev_release:
        url = "https://github.com/eupnea-linux/chromeos-kernel/releases/download/dev-build/"
    else:
        url = "https://github.com/eupnea-linux/chromeos-kernel/releases/latest/download/"

    # download kernel files
    try:
        match kernel_type:
            case "mainline":
                print_status("Downloading mainline kernel")
                url = "https://github.com/eupnea-linux/mainline-kernel/releases/latest/download/"
                if "bzImage" in files:
                    urlretrieve(f"{url}bzImage-stable", filename="/tmp/depthboot-build/bzImage")
                if "modules" in files:
                    urlretrieve(f"{url}modules-stable.tar.xz", filename="/tmp/depthboot-build/modules.tar.xz")
                if "headers" in files:
                    urlretrieve(f"{url}headers-stable.tar.xz", filename="/tmp/depthboot-build/headers.tar.xz")
            case "exp":
                print_status("Downloading experimental 5.15 kernel")
                if "bzImage" in files:
                    urlretrieve(f"{url}bzImage-exp", filename="/tmp/depthboot-build/bzImage")
                if "modules" in files:
                    urlretrieve(f"{url}modules-exp.tar.xz", filename="/tmp/depthboot-build/modules.tar.xz")
                if "headers" in files:
                    urlretrieve(f"{url}headers-exp.tar.xz", filename="/tmp/depthboot-build/headers.tar.xz")
            case "stable":
                print_status("Downloading stable 5.10 kernel")
                if "bzImage" in files:
                    urlretrieve(f"{url}bzImage-stable", filename="/tmp/depthboot-build/bzImage")
                if "modules" in files:
                    urlretrieve(f"{url}modules-stable.tar.xz", filename="/tmp/depthboot-build/modules.tar.xz")
                if "headers" in files:
                    urlretrieve(f"{url}headers-stable.tar.xz", filename="/tmp/depthboot-build/headers.tar.xz")

        print_status("Getting kernel version")
        if kernel_type == "mainline":
            url = "https://api.github.com/repos/eupnea-linux/mainline-kernel/releases/latest"
        else:
            url = "https://api.github.com/repos/eupnea-linux/chromeos-kernel/releases/latest"
        print_status("Kernel files downloaded successfully")
        return json.loads(urlopen(url).read())["tag_name"]
    except URLError:
        print_error("Failed to reach github. Check your internet connection and try again or use local files with -l")
        print_warning("Dev releases may not always be available")
        exit(1)


# download the distro rootfs
def download_rootfs(distro_name: str, distro_version: str) -> None:
    try:
        match distro_name:
            case "debian":
                print_status("Debian is downloaded later, skipping download")
            case "arch":
                print_status("Downloading latest arch rootfs from geo.mirror.pkgbuild.com")
                download_file("https://geo.mirror.pkgbuild.com/iso/latest/archlinux-bootstrap-x86_64.tar.gz",
                              "/tmp/depthboot-build/arch-rootfs.tar.gz")
            case "ubuntu" | "fedora" | "pop-os":
                print_status(f"Downloading {distro_name} rootfs, version {distro_version} from eupnea github releases")
                download_file(f"https://github.com/eupnea-linux/{distro_name}-rootfs/releases/latest/download/"
                              f"{distro_name}-rootfs-{distro_version}.tar.xz",
                              f"/tmp/depthboot-build/{distro_name}-rootfs.tar.xz")
    except URLError:
        print_error("Couldn't download rootfs. Check your internet connection and try again. If the error persists, "
                    "create an issue with the distro and version in the name")
        exit(1)


# TODO: Figure out if this is actually necessary or if linux-firmware is enough
# Download firmware for later
def download_firmware() -> None:
    print_status("Downloading chromeos firmware")
    try:
        bash("git clone --depth=1 https://chromium.googlesource.com/chromiumos/third_party/linux-firmware/ "
             "/tmp/depthboot-build/firmware")
    except URLError:
        print_error("Couldn't download firmware. Check your internet connection and try again.")
        exit(1)


# Create, mount, partition the img and flash the eupnea kernel
def prepare_img(distro_name: str, img_size) -> Tuple[str, str]:
    print_status("Preparing image")
    try:
        bash(f"fallocate -l {img_size}G depthboot.img")
    except subprocess.CalledProcessError:  # try fallocate, if it fails use dd
        bash(f"dd if=/dev/zero of=depthboot.img status=progress bs=1024 count={img_size * 1000000}")

    print_status("Mounting empty image")
    mnt_point = bash("losetup -f --show depthboot.img")
    if mnt_point == "":
        print_error("Failed to mount image")
        exit(1)
    return partition_and_flash_kernel(mnt_point, False, distro_name)


# Prepare USB/SD-card
def prepare_usb_sd(device: str, distro_name: str) -> Tuple[str, str]:
    print_status("Preparing USB/SD-card")

    # fix device name if needed
    if device.endswith("/") or device.endswith("1") or device.endswith("2"):
        device = device[:-1]
    # add /dev/ to device name, if needed
    if not device.startswith("/dev/"):
        device = f"/dev/{device}"

    # unmount all partitions
    with contextlib.suppress(subprocess.CalledProcessError):
        bash(f"umount -lf {device}*")
    if device.__contains__("mmcblk"):  # sd card
        return partition_and_flash_kernel(device, False, distro_name)
    else:
        return partition_and_flash_kernel(device, True, distro_name)


def partition_and_flash_kernel(mnt_point: str, write_usb: bool, distro_name: str) -> Tuple[str, str]:
    print_status("Preparing device/image partition")

    # Determine rootfs part name
    rootfs_mnt = f"{mnt_point}3" if write_usb else f"{mnt_point}p3"
    # remove pre-existing partition table from storage device
    bash(f"wipefs -af {mnt_point}")

    # format as per depthcharge requirements,
    # READ: https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices
    bash(f"parted -s {mnt_point} mklabel gpt")
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Kernel 1 65")  # kernel partition
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Kernel 65 129")  # reserve kernel partition
    bash(f"parted -s -a optimal {mnt_point} unit mib mkpart Root 129 100%")  # rootfs partition
    bash(f"cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 {mnt_point}")  # set kernel flags
    bash(f"cgpt add -i 2 -t kernel -S 1 -T 5 -P 1 {mnt_point}")  # set backup kernel flags

    # get uuid of rootfs partition
    rootfs_partuuid = bash(f"blkid -o value -s PARTUUID {rootfs_mnt}")

    # write PARTUUID to kernel flags and save it as a file
    with open(f"configs/cmdlines/{distro_name}.flags", "r") as flags:
        temp_cmdline = flags.read().replace("insert_partuuid", rootfs_partuuid).strip()
    with open("kernel.flags", "w") as config:
        config.write(temp_cmdline)

    print_status("Flashing kernel to device/image")
    # Sign kernel
    bash("futility vbutil_kernel --arch x86_64 --version 1 --keyblock /usr/share/vboot/devkeys/kernel.keyblock"
         + " --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk --bootloader kernel.flags" +
         " --config kernel.flags --vmlinuz /tmp/depthboot-build/bzImage --pack /tmp/depthboot-build/bzImage.signed")

    # Flash kernel
    if write_usb:
        # if writing to usb, then no p in partition name
        bash(f"dd if=/tmp/depthboot-build/bzImage.signed of={mnt_point}1")
        bash(f"dd if=/tmp/depthboot-build/bzImage.signed of={mnt_point}2")  # Backup kernel
    else:
        # image is a loop device -> needs p in part name
        bash(f"dd if=/tmp/depthboot-build/bzImage.signed of={mnt_point}p1")
        bash(f"dd if=/tmp/depthboot-build/bzImage.signed of={mnt_point}p2")  # Backup kernel

    print_status("Formatting rootfs part")
    # Create rootfs ext4 partition
    bash(f"yes 2>/dev/null | mkfs.ext4 {rootfs_mnt}")  # 2>/dev/null is to supress yes broken pipe warning

    # Mount rootfs partition
    bash(f"mount {rootfs_mnt} /mnt/depthboot")

    print_status("Device/image preparation complete")
    return mnt_point, rootfs_partuuid  # return loop device, so it can be unmounted at the end


# extract the rootfs to /mnt/depthboot
def extract_rootfs(distro_name: str, distro_version: str) -> None:
    print_status("Extracting rootfs")
    match distro_name:
        case "debian":
            print_status("Debootstraping Debian into /mnt/depthboot")
            # debootstrapping directly to /mnt/depthboot
            debian_result = bash(f"debootstrap {distro_version} /mnt/depthboot https://deb.debian.org/debian/")
            if debian_result.__contains__("Couldn't download packages:"):
                print_error("Debian Debootstrap failed, check your internet connection or try again later")
                exit(1)
        case "arch":
            print_status("Extracting arch rootfs")
            mkdir("/tmp/depthboot-build/arch-rootfs")
            extract_file("/tmp/depthboot-build/arch-rootfs.tar.gz", "/tmp/depthboot-build/arch-rootfs")
            cpdir("/tmp/depthboot-build/arch-rootfs/root.x86_64/", "/mnt/depthboot/")
        case "pop-os" | "ubuntu" | "fedora":
            print_status(f"Extracting {distro_name} rootfs")
            extract_file(f"/tmp/depthboot-build/{distro_name}-rootfs.tar.xz", "/mnt/depthboot")
    print_status("\n" + "Rootfs extraction complete")


# Configure distro agnostic options
def post_extract(build_options, kernel_type: str, kernel_version: str, dev_release: bool) -> None:
    print_status("Applying distro agnostic configuration")

    # Extract modules
    print_status("Extracting kernel modules")
    rmdir("/mnt/depthboot/lib/modules")  # remove any preinstalled modules
    mkdir("/mnt/depthboot/lib/modules")
    extract_file("/tmp/depthboot-build/modules.tar.xz", "/mnt/depthboot/lib/modules/")

    # Extract kernel headers
    print_status("Extracting kernel headers")
    dir_kernel_version = bash("ls /mnt/depthboot/lib/modules/").strip()  # get modules dir name
    rmdir(f"/mnt/depthboot/usr/src/linux-headers-{dir_kernel_version}", keep_dir=False)  # remove old headers
    mkdir(f"/mnt/depthboot/usr/src/linux-headers-{dir_kernel_version}", create_parents=True)
    extract_file("/tmp/depthboot-build/headers.tar.xz", f"/mnt/depthboot/usr/src/linux-headers-{dir_kernel_version}")
    # use chroot for correct symlink
    chroot(f"ln -s /usr/src/linux-headers-{dir_kernel_version}/ /lib/modules/{dir_kernel_version}/build")

    # Create a temporary resolv.conf for internet inside the chroot
    mkdir("/mnt/depthboot/run/systemd/resolve", create_parents=True)  # dir doesnt exist coz systemd didnt run
    open("/mnt/depthboot/run/systemd/resolve/stub-resolv.conf", "w").close()  # create empty file for mount
    # Bind mount host resolv.conf to chroot resolv.conf.
    # If chroot /etc/resolv.conf is a symlink, then it will be resolved to the real file and bind mounted
    # This is needed for internet inside the chroot
    bash("mount --bind /etc/resolv.conf /mnt/depthboot/etc/resolv.conf")

    # create depthboot settings file for postinstall scripts to read
    with open("configs/eupnea.json", "r") as settings_file:
        settings = json.load(settings_file)
    settings["kernel_type"] = kernel_type
    settings["kernel_version"] = kernel_version
    settings["kernel_dev"] = dev_release
    settings["distro_name"] = build_options["distro_name"]
    settings["distro_version"] = build_options["distro_version"]
    settings["de_name"] = build_options["de_name"]
    if build_options["device"] != "image":
        settings["install_type"] = "direct"
    with open("/mnt/depthboot/etc/eupnea.json", "w") as settings_file:
        json.dump(settings, settings_file)

    print_status("Fixing sleep")
    # disable hibernation aka S3 sleep, READ more: https://eupnea-linux.github.io/main.html#/pages/bootlock
    # This fix is removed if the user installs to internal
    mkdir("/mnt/depthboot/etc/systemd/")  # just in case systemd path doesn't exist
    with open("/mnt/depthboot/etc/systemd/sleep.conf", "a") as conf:
        conf.write("SuspendState=freeze\nHibernateState=freeze\n")

    print_status("Fixing screen rotation")
    # Install hwdb file to fix auto rotate being flipped on some devices
    cpfile("configs/hwdb/61-sensor.hwdb", "/mnt/depthboot/etc/udev/hwdb.d/61-sensor.hwdb")
    chroot("systemd-hwdb update")

    if build_options["distro_name"] == "fedora":
        print_status("Enabling resolved.conf systemd service")
        # systemd-resolved.service needed to create /etc/resolv.conf link. Not enabled by default on fedora
        # on other distros networkmanager takes care of this
        chroot("systemctl enable systemd-resolved")

    print_status("Enable modules autoloading")
    # Enable loading modules needed for depthboot
    # TODO: Remove for v1.2.0 release
    cpfile("configs/eupnea-modules.conf", "/mnt/depthboot/etc/modules-load.d/eupnea-modules.conf")

    # Do not pre-setup gnome, as there is a nice gui first time setup on first boot
    # TODO: Change to gnome
    if build_options["de_name"] != "popos":
        print_status("Configuring user")
        username = build_options["username"]  # quotes interfere with functions below
        chroot(f"useradd --create-home --shell /bin/bash {username}")
        password = build_options["password"]  # quotes interfere with functions below
        chroot(f"echo '{username}:{password}' | chpasswd")
        match build_options["distro_name"]:
            case "ubuntu" | "debian":
                chroot(f"usermod -aG sudo {username}")
            case "arch" | "fedora":
                chroot(f"usermod -aG wheel {username}")

        # set timezone build system timezone on device
        # In some environments(Crouton), the timezone is not set -> ignore in that case
        with contextlib.suppress(subprocess.CalledProcessError):
            host_time_zone = bash("file /etc/localtime")  # read host timezone link
            host_time_zone = host_time_zone[host_time_zone.find("/usr/share/zoneinfo/"):].strip()  # get actual timezone
            chroot(f"ln -sf {host_time_zone} /etc/localtime")
        print_status("Distro agnostic configuration complete")


# post extract and distro config
def post_config(de_name: str, distro_name) -> None:
    if de_name != "cli":
        # Add chromebook layout. Needs to be done after installing Xorg
        print_status("Backing up default keymap and setting Chromebook layout")
        cpfile("/mnt/depthboot/usr/share/X11/xkb/symbols/pc", "/mnt/depthboot/usr/share/X11/xkb/symbols/pc.default")
        cpfile("configs/xkb/xkb.chromebook", "/mnt/depthboot/usr/share/X11/xkb/symbols/pc")

    # copy previously downloaded firmware
    print_status("Copying google firmware")
    cpdir("/tmp/depthboot-build/firmware", "/mnt/depthboot/lib/firmware")

    # Enable postinstall service
    print_status("Enabling postinstall service")
    chroot("systemctl enable eupnea-postinstall.service")

    # Fedora requires all files to be relabled for SELinux to work
    # If this is not done, SELinux will prevent users from logging in
    if distro_name == "fedora":
        print_status("Relabeling files for SELinux")

        # copy /proc files needed for fixfiles
        mkdir("/mnt/depthboot/proc/self")
        cpfile("configs/selinux/mounts", "/mnt/depthboot/proc/self/mounts")
        cpfile("configs/selinux/mountinfo", "/mnt/depthboot/proc/self/mountinfo")

        # copy /sys files needed for fixfiles
        mkdir("/mnt/depthboot/sys/fs/selinux/initial_contexts/", create_parents=True)
        cpfile("configs/selinux/unlabeled", "/mnt/depthboot/sys/fs/selinux/initial_contexts/unlabeled")

        # Backup original selinux
        cpfile("/mnt/depthboot/usr/sbin/fixfiles", "/mnt/depthboot/usr/sbin/fixfiles.bak")
        # Copy patched fixfiles script
        cpfile("configs/selinux/fixfiles", "/mnt/depthboot/usr/sbin/fixfiles")

        chroot("/sbin/fixfiles -T 0 restore")

        # Restore original fixfiles
        cpfile("/mnt/depthboot/usr/sbin/fixfiles.bak", "/mnt/depthboot/usr/sbin/fixfiles")
        rmfile("/mnt/depthboot/usr/sbin/fixfiles.bak")

    # Unmount everything
    with contextlib.suppress(subprocess.CalledProcessError):
        bash("umount -flR /mnt/depthboot/*")  # recursive unmount

    # Unmount resolv.conf
    with contextlib.suppress(subprocess.CalledProcessError):
        bash("umount -fl /mnt/depthboot/etc/resolv.conf")

    # Clean all temporary files from image/sd-card to reduce its size
    rmdir("/mnt/depthboot/tmp")
    rmdir("/mnt/depthboot/var/tmp")
    rmdir("/mnt/depthboot/var/cache")
    rmdir("/mnt/depthboot/proc")
    rmdir("/mnt/depthboot/run")
    rmdir("/mnt/depthboot/sys")
    rmdir("/mnt/depthboot/lost+found")
    rmdir("/mnt/depthboot/dev")


# chroot command
def chroot(command: str) -> str:
    return bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')


# The main build script
def start_build(verbose: bool, local_path, kernel_type: str, dev_release: bool, build_options, img_size: int = 10,
                no_download_progress: bool = False, no_shrink: bool = False) -> None:
    if no_download_progress:
        disable_download_progress()  # disable download progress bar for non-interactive shells
    set_verbose(verbose)
    atexit.register(exit_handler)
    print_status("Starting build")

    prepare_host(build_options["distro_name"])

    if local_path is None:  # default
        kernel_version = download_kernel(kernel_type, dev_release)
        download_rootfs(build_options["distro_name"], build_options["distro_version"])
        download_firmware()
    else:  # if local path is specified, copy files from it, instead of downloading from the internet
        print_status("Copying local files to /tmp/depthboot-build")
        # clean local path string
        local_path_posix = local_path if local_path.endswith("/") else f"{local_path}/"
        # copy kernel files
        kernel_files = ["bzImage", "modules.tar.xz", "headers.tar.xz", ]
        for file in kernel_files:
            try:
                cpfile(f"{local_path_posix}{file}", f"/tmp/depthboot-build/{file}")
                kernel_version = "unknown"
            except FileNotFoundError:
                print_error(f"File {file} not found in {local_path}, attempting to download")
                kernel_version = download_kernel(kernel_type, dev_release, [file])

        # copy distro agnostic files
        dirs = {
            "firmware": download_firmware,
        }
        for directory in dirs:
            try:
                cpdir(f"{local_path_posix}{directory}", f"/tmp/depthboot-build/{directory}")
            except FileNotFoundError:
                print_error(f"Directory {directory} not found in {local_path}, attempting to download")
                dirs[directory]()

        # copy distro rootfs
        distro_rootfs = {
            # distro_name:[cp function type,filename]
            "ubuntu": [cpfile, "ubuntu-rootfs.tar.xz"],
            "debian": [cpdir, "debian"],
            "arch": [cpfile, "arch-rootfs.tar.gz"],
            "fedora": [cpfile, "fedora-rootfs.tar.xz"],
            "pop-os": [cpfile, "pop-os.iso"]
        }
        if build_options["distro_name"] == "pop-os":
            # symlink instead of copying whole iso
            bash(f"ln -s {local_path_posix}pop-os.iso /tmp/depthboot-build/pop-os.iso")
        try:
            distro_rootfs[build_options["distro_name"]][0](
                f"{local_path_posix}{distro_rootfs[build_options['distro_name']][1]}",
                f"/tmp/depthboot-build/{distro_rootfs[build_options['distro_name']][1]}")
        except FileNotFoundError:
            print_error(f"File {distro_rootfs[build_options['distro_name']][1]} not found in {local_path}, "
                        f"attempting to download")
            download_rootfs(build_options["distro_name"], build_options["distro_version"])

    # Setup device
    if build_options["device"] == "image":
        output_temp = prepare_img(build_options["distro_name"], img_size)
    else:
        output_temp = prepare_usb_sd(build_options["device"], build_options["distro_name"])
    root_partuuid = output_temp[1]
    global img_mnt
    img_mnt = output_temp[0]
    # Extract rootfs and configure distro agnostic settings
    extract_rootfs(build_options["distro_name"], build_options["distro_version"])
    post_extract(build_options, kernel_type, kernel_version, dev_release)

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
    distro.config(build_options["de_name"], build_options["distro_version"], verbose)

    post_config(build_options["de_name"], build_options["distro_name"])

    print_status("Unmounting image/device")

    bash("sync")  # write all pending changes to usb

    # unmount image/device from mnt
    with contextlib.suppress(subprocess.CalledProcessError):
        bash("umount -lf /mnt/depthboot")  # umount mountpoint
    sleep(5)  # wait for umount to finish

    # unmount image/device completely from system
    # on crostini umount fails for some reason
    with contextlib.suppress(subprocess.CalledProcessError):
        bash(f"umount -lf {img_mnt}p*")  # umount all partitions from image
    with contextlib.suppress(subprocess.CalledProcessError):
        bash(f"umount -lf {img_mnt}*")  # umount all partitions from usb/sd-card

    if build_options["device"] == "image":
        try:
            with open("/sys/devices/virtual/dmi/id/product_name", "r") as file:
                product_name = file.read().strip()
        except FileNotFoundError:  # WSL doesnt have dmi data
            product_name = ""
        # TODO: Fix shrinking on Crostini
        if product_name != "crosvm" and not no_shrink:
            # Shrink image to actual size
            print_status("Shrinking image")
            bash(f"e2fsck -fpv {img_mnt}p3")  # Force check filesystem for errors
            bash(f"resize2fs -f -M {img_mnt}p3")
            block_count = int(bash(f"dumpe2fs -h {img_mnt}p3 | grep 'Block count:'")[12:].split()[0])
            actual_fs_in_bytes = block_count * 4096
            # the kernel part is always the same size -> sector amount: 131072 * 512 => 67108864 bytes
            # There are 2 kernel partitions -> 67108864 bytes * 2 = 134217728 bytes
            actual_fs_in_bytes += 134217728
            actual_fs_in_bytes += 20971520  # add 20mb for linux to be able to boot properly
            bash(f"truncate --size={actual_fs_in_bytes} ./depthboot.img")
        if product_name == "crosvm":
            # rename the image to .bin for the chromeos recovery utility to be able to flash it
            bash("mv ./depthboot.img ./depthboot.bin")

        bash(f"losetup -d {img_mnt}")  # unmount image from loop device
        print_header(f"The ready-to-boot {build_options['distro_name'].capitalize()} Depthboot image is located at "
                     f"{get_full_path('.')}/depthboot.img")
    else:
        print_header(f"USB/SD-card is ready to boot {build_options['distro_name'].capitalize()}")
        print_header("It is safe to remove the USB-drive/SD-card now.")
    print_header("Please report any bugs/issues on GitHub or on the Discord server.")


if __name__ == "__main__":
    print_error("Do not run this file directly. Instead, run main.py")
