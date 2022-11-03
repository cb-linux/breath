#!/usr/bin/env python3

from typing import Tuple
from urllib.request import urlretrieve, urlopen
from urllib.error import URLError
import json

from functions import *


# Clean old depthboot files from /tmp
def prepare_host(de_name: str) -> None:
    print_status("Cleaning + preparing host system")
    rmdir("/tmp/depthboot-build")
    mkdir("/tmp/depthboot-build", create_parents=True)

    print_status("Creating mount points")
    try:
        bash("umount -lf /mnt/depthboot")  # just in case
        sleep(5)  # wait for umount to finish
    except subprocess.CalledProcessError:
        print("Failed to unmount /mnt/depthboot, ignore")
        pass
    rmdir("/mnt/depthboot")
    mkdir("/mnt/depthboot", create_parents=True)

    rmfile("depthboot.img")
    rmfile("kernel.flags")

    # Install dependencies
    install_kernel_packages()

    # TODO: only install if building image
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
def download_kernel(kernel_type: str, dev_release: bool, files: list = ["bzImage", "modules", "headers"]) -> str:
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
                if "bzImage" in files:
                    urlretrieve(f"{url}bzImage-stable", filename="/tmp/depthboot-build/bzImage")
                if "modules" in files:
                    urlretrieve(f"{url}modules-stable.tar.xz", filename="/tmp/depthboot-build/modules.tar.xz")
                if "headers" in files:
                    urlretrieve(f"{url}headers-stable.tar.xz", filename="/tmp/depthboot-build/headers.tar.xz")
            case "alt":
                print_status("Downloading alt kernel")
                if "bzImage" in files:
                    urlretrieve(f"{url}bzImage-alt", filename="/tmp/depthboot-build/bzImage")
                if "modules" in files:
                    urlretrieve(f"{url}modules-alt.tar.xz", filename="/tmp/depthboot-build/modules.tar.xz")
                if "headers" in files:
                    urlretrieve(f"{url}headers-alt.tar.xz", filename="/tmp/depthboot-build/headers.tar.xz")
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
            url = "https://api.github.com/repos/eupnea-linux/kernel/releases/latest"
        return json.loads(urlopen(url).read())["tag_name"]
    except URLError:
        print_error("Failed to reach github. Check your internet connection and try again or use local files with -l")
        print_warning("Dev releases may not always be available")
        exit(1)

    stop_progress()  # stop fake progress
    print_status("Kernel files downloaded successfully")


# download the distro rootfs
def download_rootfs(distro_name: str, distro_version: str) -> None:
    try:
        match distro_name:
            case "ubuntu":
                print_status(f"Downloading ubuntu rootfs version: {distro_version} from github")
                start_download_progress("/tmp/depthboot-build/ubuntu-rootfs.tar.xz")
                urlretrieve(f"https://github.com/eupnea-linux/ubuntu-rootfs/releases/latest/download/ubuntu-rootfs-"
                            f"{distro_version}.tar.xz", filename="/tmp/depthboot-build/ubuntu-rootfs.tar.xz")
                stop_download_progress()
            case "debian":
                print_status("Debian is downloaded later, skipping download")
            case "arch":
                print_status("Downloading latest arch rootfs")
                start_download_progress("/tmp/depthboot-build/arch-rootfs.tar.gz")
                urlretrieve("https://geo.mirror.pkgbuild.com/iso/latest/archlinux-bootstrap-x86_64.tar.gz",
                            filename="/tmp/depthboot-build/arch-rootfs.tar.gz")
                stop_download_progress()
            case "fedora":
                print_status(f"Downloading fedora rootfs version: {distro_version} from github")
                start_download_progress("/tmp/depthboot-build/fedora-rootfs.tar.xz")
                urlretrieve(f"https://github.com/eupnea-linux/fedora-rootfs/releases/latest/download/fedora-rootfs-"
                            f"{distro_version}.tar.xz", filename="/tmp/depthboot-build/fedora-rootfs.tar.xz")
                stop_download_progress()
            case "pop-os":
                print_status(f"Downloading pop-os rootfs from github")
                start_download_progress("/tmp/depthboot-build/popos-rootfs.tar.xz")
                urlretrieve(
                    f"https://github.com/eupnea-linux/popos-rootfs/releases/latest/download/popos-rootfs.tar.xz",
                    filename="/tmp/depthboot-build/popos-rootfs.tar.xz")
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
             "/tmp/depthboot-build/firmware")
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
             "/tmp/depthboot-build/postinstall-scripts")
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
             "/tmp/depthboot-build/audio-scripts")
    except URLError:
        print_error("Couldn't download audio scripts. Check your internet connection and try again.")
        exit(1)
    stop_progress()  # stop fake progress


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
         " --config kernel.flags --vmlinuz /tmp/depthboot-build/bzImage --pack /tmp/depthboot-build/bzImage.signed")

    # Flash kernel
    if write_usb:
        # if writing to usb, then no p in partition name
        bash(f"dd if=/tmp/depthboot-build/bzImage.signed of={mnt_point}1")
    else:
        # image is a loop device -> needs p in part name
        bash(f"dd if=/tmp/depthboot-build/bzImage.signed of={mnt_point}p1")

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
        case "ubuntu":
            print_status("Extracting ubuntu rootfs")
            # --checkpoint is for printing real tar progress
            bash("tar xfp /tmp/depthboot-build/ubuntu-rootfs.tar.xz -C /mnt/depthboot --checkpoint=.10000")
        case "debian":
            print_status("Debootstraping Debian into /mnt/depthboot")
            start_progress()  # start fake progress
            # debootstrapping directly to /mnt/depthboot
            debian_result = bash("debootstrap stable /mnt/depthboot https://deb.debian.org/debian/")
            stop_progress()  # stop fake progress
            if debian_result.__contains__("Couldn't download packages:"):
                print_error("Debian Debootstrap failed, check your internet connection or try again later")
                exit(1)
        case "arch":
            print_status("Extracting arch rootfs")
            mkdir("/tmp/depthboot-build/arch-rootfs")
            bash("tar xfp /tmp/depthboot-build/arch-rootfs.tar.gz -C /tmp/depthboot-build/arch-rootfs "
                 "--checkpoint=.10000")
            start_progress(force_show=True)  # start fake progress
            cpdir("/tmp/depthboot-build/arch-rootfs/root.x86_64/", "/mnt/depthboot/")
            stop_progress(force_show=True)  # stop fake progress
        case "fedora":
            print_status("Extracting fedora rootfs")
            # --checkpoint is for printing real tar progress
            bash("tar xfp /tmp/depthboot-build/fedora-rootfs.tar.xz -C /mnt/depthboot --checkpoint=.10000")
        case "pop-os":
            print_status("Extracting popos rootfs")
            # --checkpoint is for printing real tar progress
            bash("tar xfp /tmp/depthboot-build/popos-rootfs.tar.xz -C /mnt/depthboot --checkpoint=.10000")

    print_status("\n" + "Rootfs extraction complete")


# Configure distro agnostic options
def post_extract(build_options, kernel_type: str, kernel_version: str, dev_release: bool) -> None:
    print_status("Applying distro agnostic configuration")

    # Extract modules
    print_status("Extracting kernel modules")
    rmdir("/mnt/depthboot/lib/modules")  # remove all old modules
    mkdir("/mnt/depthboot/lib/modules")
    bash(f"tar xpf /tmp/depthboot-build/modules.tar.xz -C /mnt/depthboot/lib/modules/ --checkpoint=.10000")
    print("")  # break line after tar

    # Extract kernel headers
    print_status("Extracting kernel headers")
    dir_kernel_version = bash(f"ls /mnt/depthboot/lib/modules/").strip()  # get modules dir name
    rmdir(f"/mnt/depthboot/usr/src/linux-headers-{dir_kernel_version}", keep_dir=False)  # remove old headers
    mkdir(f"/mnt/depthboot/usr/src/linux-headers-{dir_kernel_version}", create_parents=True)
    bash(f"tar xpf /tmp/depthboot-build/headers.tar.xz -C /mnt/depthboot/usr/src/linux-headers-{dir_kernel_version}/ "
         f"--checkpoint=.10000")
    print("")  # break line after tar
    chroot(f"ln -s /usr/src/linux-headers-{dir_kernel_version}/ "
           f"/lib/modules/{dir_kernel_version}/build")  # use chroot for correct symlink

    # Create a temporary resolv.conf for internet inside the chroot
    mkdir("/mnt/depthboot/run/systemd/resolve", create_parents=True)  # dir doesnt exist coz systemd didnt run
    cpfile("/etc/resolv.conf",
           "/mnt/depthboot/run/systemd/resolve/stub-resolv.conf")  # copy hosts resolv.conf to chroot

    # Set device hostname
    with open("/mnt/depthboot/etc/hostname", "w") as hostname_file:
        hostname_file.write(build_options["hostname"] + "\n")

    # Copy eupnea scripts and config
    print_status("Copying eupnea scripts and configs")
    # Copy postinstall scripts
    for file in Path("/tmp/depthboot-build/postinstall-scripts").iterdir():
        if file.is_file():
            if file.name == "LICENSE" or file.name == "README.md" or file.name == ".gitignore":
                continue  # dont copy license, readme and gitignore
            else:
                cpfile(file.absolute().as_posix(), f"/mnt/depthboot/usr/local/bin/{file.name}")
    # copy audio setup script
    cpfile("/tmp/depthboot-build/audio-scripts/setup-audio", "/mnt/depthboot/usr/local/bin/setup-audio")
    # copy functions file
    cpfile("functions.py", "/mnt/depthboot/usr/local/bin/functions.py")
    chroot("chmod 755 /usr/local/bin/*")  # make scripts executable in system

    # copy configs
    mkdir("/mnt/depthboot/etc/eupnea")
    cpdir("configs", "/mnt/depthboot/etc/eupnea")  # eupnea-builder configs
    cpdir("/tmp/depthboot-build/postinstall-scripts/configs", "/mnt/depthboot/etc/eupnea")  # postinstall configs
    cpdir("/tmp/depthboot-build/audio-scripts/configs", "/mnt/depthboot/etc/eupnea")  # audio configs

    # create depthboot settings file for postinstall scripts to read
    with open("configs/eupnea.json", "r") as settings_file:
        settings = json.load(settings_file)
    settings["kernel_type"] = kernel_type
    settings["kernel_version"] = kernel_version
    settings["kernel_dev"] = dev_release
    settings["distro_name"] = build_options["distro_name"]
    settings["distro_version"] = build_options["distro_version"]
    settings["de_name"] = build_options["de_name"]
    if not build_options["device"] == "image":
        settings["install_type"] = "direct"
    with open("/mnt/depthboot/etc/eupnea.json", "w") as settings_file:
        json.dump(settings, settings_file)

    print_status("Fixing sleep")
    # disable hibernation aka S4 sleep, READ: https://eupnea-linux.github.io/docs.html#/pages/bootlock
    # TODO: Fix sleep, maybe
    mkdir("/mnt/depthboot/etc/systemd/")  # just in case systemd path doesn't exist
    with open("/mnt/depthboot/etc/systemd/sleep.conf", "a") as conf:
        conf.write("SuspendState=freeze\nHibernateState=freeze\n")

    # Enable loading modules needed for depthboot
    cpfile("configs/eupnea-modules.conf", "/mnt/depthboot/etc/modules-load.d/eupnea-modules.conf")

    username = build_options["username"]  # quotes interfere with functions below
    password = build_options["password"]  # quotes interfere with functions below

    # Do not pre-setup gnome, as there is a nice gui first time setup on first boot
    # TODO: Change to gnome
    if not build_options["de_name"] == "popos":
        print_status("Configuring user")
        chroot(f"useradd --create-home --shell /bin/bash {username}")
        # TODO: Fix ) and ( crashing chpasswd
        chroot(f'echo "{username}:{password}" | chpasswd')
        match build_options["distro_name"]:
            case "ubuntu" | "debian":
                chroot(f"usermod -aG sudo {username}")
            case "arch" | "fedora":
                chroot(f"usermod -aG wheel {username}")

        # set timezone build system timezone on device
        host_time_zone = bash("file /etc/localtime")  # read host timezone link
        host_time_zone = host_time_zone[host_time_zone.find("/usr/share/zoneinfo/"):].strip()  # get actual timezone
        chroot(f"ln -sf {host_time_zone} /etc/localtime")

        print_status("Distro agnostic configuration complete")


# post extract and distro config
def post_config(rebind_search: bool, de_name: str, distro_name) -> None:
    if not de_name == "cli":
        # Add chromebook layout. Needs to be done after install Xorg
        print_status("Backing up default keymap and setting Chromebook layout")
        cpfile("/mnt/depthboot/usr/share/X11/xkb/symbols/pc", "/mnt/depthboot/usr/share/X11/xkb/symbols/pc.default")
        cpfile("configs/xkb/xkb.chromebook", "/mnt/depthboot/usr/share/X11/xkb/symbols/pc")
        if rebind_search:  # rebind search key to caps lock
            print("Rebinding search key to Caps Lock")
            cpfile("/mnt/depthboot/usr/share/X11/xkb/keycodes/evdev",
                   "/mnt/depthboot/usr/share/X11/xkb/keycodes/evdev.default")

    # Add postinstall service
    print_status("Adding postinstall service")
    cpfile("configs/postinstall.service", "/mnt/depthboot/etc/systemd/system/postinstall.service")
    chroot("systemctl enable postinstall.service")

    # copy previously downloaded firmware
    print_status("Copying google firmware")
    rmdir("/mnt/depthboot/lib/firmware")
    start_progress(force_show=True)  # start fake progress
    cpdir("/tmp/depthboot-build/firmware", "/mnt/depthboot/lib/firmware")
    stop_progress(force_show=True)  # stop fake progress

    if distro_name == "fedora":
        # Fedora requires all files to be relabled for SELinux to work
        # If this is not done, SELinux will prevent users from logging in
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


# chroot command
def chroot(command: str) -> str:
    return bash(f'chroot /mnt/depthboot /bin/bash -c "{command}"')


# The main build script
def start_build(verbose: bool, local_path, kernel_type: str, dev_release: bool, build_options, img_size: int = 10,
                no_download_progress: bool = False, no_shrink: bool = False) -> None:
    if no_download_progress:
        disable_download_progress()  # disable download progress bar for non-interactive shells
    set_verbose(verbose)
    print_status("Starting build")

    prepare_host(build_options["distro_name"])

    if local_path is None:  # default
        kernel_version = download_kernel(kernel_type, dev_release)
        download_rootfs(build_options["distro_name"], build_options["distro_version"])
        download_firmware()
        download_postinstall_scripts()
        download_audio_scripts()
    else:  # if local path is specified, copy files from it, instead of downloading from the internet
        print_status("Copying local files to /tmp/depthboot-build")
        # clean local path string
        if not local_path.endswith("/"):
            local_path_posix = f"{local_path}/"
        else:
            local_path_posix = local_path

        # copy kernel files
        kernel_files = ["bzImage", "modules", "headers", ]
        for file in kernel_files:
            try:
                cpfile(f"{local_path_posix}{file}", f"/tmp/depthboot-build/{file}")
            except FileNotFoundError:
                print_error(f"File {file} not found in {local_path}, attempting to download")
                kernel_version = download_kernel(kernel_type, dev_release, [file])

        # copy distro agnostic files
        dirs = {
            "firmware": download_firmware,
            "postinstall-scripts": download_postinstall_scripts,
            "audio-scripts": download_audio_scripts
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
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]
    else:
        output_temp = prepare_usb(build_options["device"], build_options["distro_name"])
        img_mnt = output_temp[0]
        root_partuuid = output_temp[1]

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
    distro.config(build_options["de_name"], build_options["distro_version"], build_options["username"], root_partuuid,
                  verbose)

    post_config(build_options["rebind_search"], build_options["de_name"], build_options["distro_name"])

    # Post-install cleanup
    print_status("Cleaning up host system after build")

    # /mnt/depthboot doesn't unmount on first try and e2fsck throws an error, therefore its unmounted twice
    try:
        bash("umount -f /mnt/depthboot")  # umount mountpoint
    except subprocess.CalledProcessError as error:  # on crostini umount fails for some reason
        if verbose:
            print(error)
    sleep(5)  # wait for umount to finish
    try:
        bash("umount -f /mnt/depthboot")  # umount mountpoint again
    except subprocess.CalledProcessError as error:  # on crostini umount fails for some reason
        if verbose:
            print(error)
    if build_options["device"] == "image":
        try:
            with open("/sys/devices/virtual/dmi/id/product_name", "r") as file:
                product_name = file.read().strip()
        except FileNotFoundError:  # WSL doesnt have dmi data
            product_name = ""
        # TODO: Fix shrinking on Crostini
        if not product_name == "crosvm" and not no_shrink:
            # Shrink image to actual size
            print_status("Shrinking image")
            bash(f"e2fsck -fpv {img_mnt}p2")  # Force check filesystem for errors
            bash(f"resize2fs -f -M {img_mnt}p2")
            block_count = int(bash(f"dumpe2fs -h {img_mnt}p2 | grep 'Block count:'")[12:].split()[0])
            actual_fs_in_bytes = block_count * 4096
            # the kernel part is always the same size -> sector amount: 131072 * 512 => 67108864 bytes
            actual_fs_in_bytes += 67108864
            actual_fs_in_bytes += 102400  # add 100kb for linux to be able to boot
            bash(f"truncate --size={actual_fs_in_bytes} ./depthboot.img")
        if product_name == "crosvm":
            # rename the image to .bin for the chromeos recovery utility to be able to flash it
            bash(f"mv ./depthboot.img ./depthboot.bin")

        bash(f"losetup -d {img_mnt}")
        print_header(f"The ready-to-boot Depthboot image is located at {get_full_path('.')}/depthboot.img")
    else:
        print_header(f"USB/SD-card is ready to boot {build_options['distro_name'].capitalize()}")
        print_header("It is safe to remove the USB-drive/SD-card now.")
    print_header("Please report any bugs/issues on GitHub or on the Discord server.")


if __name__ == "__main__":
    print_error("Do not run this file directly. Instead, run main.py")
