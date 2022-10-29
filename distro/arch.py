from functions import *


def config(de_name: str, distro_version: str, username: str, root_partuuid: str, verbose: bool) -> None:
    set_verbose(verbose)
    print_status("Configuring Arch")

    # Uncomment worldwide arch mirror
    with open("/mnt/depthboot/etc/pacman.d/mirrorlist", "r") as read:
        mirrors = read.readlines()
    # Uncomment first worldwide mirror
    mirrors[6] = mirrors[6][1:]
    with open("/mnt/depthboot/etc/pacman.d/mirrorlist", "w") as write:
        write.writelines(mirrors)

    # Apply temporary fix for pacman
    bash("mount --bind /mnt/depthboot /mnt/depthboot")
    with open("/mnt/depthboot/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # temporarily comment out CheckSpace, coz Pacman fails to check available storage space when run from a chroot
    temp_pacman[34] = f"#{temp_pacman[34]}"
    with open("/mnt/depthboot/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    print_status("Preparing pacman")
    chroot("pacman-key --init")
    chroot("pacman-key --populate archlinux")
    chroot("pacman -Syyu --noconfirm")  # update the whole system

    print_status("Installing packages")
    start_progress()  # start fake progress
    chroot("pacman -S --noconfirm base base-devel nano networkmanager xkeyboard-config linux-firmware sudo")
    chroot("pacman -S --noconfirm git cloud-utils rsync")  # postinstall script dependencies
    stop_progress()  # stop fake progress

    print_status("Downloading and installing de, might take a while")
    start_progress()  # start fake progress
    match de_name:
        case "gnome":
            print_status("Installing GNOME")
            chroot("pacman -S --noconfirm gnome gnome-extra gnome-initial-setup")
            chroot("systemctl enable gdm.service")
        case "kde":
            print_status("Installing KDE")
            chroot("pacman -S --noconfirm plasma-meta plasma-wayland-session kde-applications packagekit-qt5")
            chroot("systemctl enable sddm.service")
        case "xfce":
            print_status("Installing Xfce")
            # no wayland support in xfce
            chroot("pacman -S --noconfirm xfce4 xfce4-goodies xorg xorg-server lightdm lightdm-gtk-greeter firefox "
                   "network-manager-applet nm-connection-editor gnome-software")
            chroot("systemctl enable lightdm.service")
        case "lxqt":
            print_status("Installing LXQt")
            chroot("pacman -S --noconfirm lxqt breeze-icons xorg xorg-server sddm firefox networkmanager-qt "
                   "network-manager-applet nm-connection-editor discover packagekit-qt5")
            chroot("systemctl enable sddm.service")
        case "deepin":
            print_status("Installing deepin")
            chroot("pacman -S --noconfirm deepin deepin-kwin deepin-extra xorg xorg-server lightdm kde-applications "
                   "firefox discover packagekit-qt5")
            # enable deepin specific login style
            with open("/mnt/depthboot/etc/lightdm/lightdm.conf", "a") as conf:
                conf.write("greeter-session=lightdm-deepin-greeter")
            chroot("systemctl enable lightdm.service")
        case "budgie":
            print_status("Installing Budgie")
            chroot("pacman -S --noconfirm budgie-desktop budgie-desktop-view budgie-screensaver budgie-control-center "
                   "lightdm lightdm-gtk-greeter xorg xorg-server network-manager-applet")
            chroot("systemctl enable lightdm.service")
        case "cli":
            print_status("Skipping desktop environment install")
        case _:
            print_error("Invalid desktop environment! Please create an issue")
            exit(1)

    stop_progress()  # stop fake progress
    print_status("Desktop environment setup complete")

    # enable networkmanager systemd service
    chroot("systemctl enable NetworkManager.service")

    # Configure sudo
    with open("/mnt/depthboot/etc/sudoers", "r") as conf:
        temp_sudoers = conf.readlines()
    # uncomment wheel group
    temp_sudoers[84] = temp_sudoers[84][2:]
    with open("/mnt/depthboot/etc/sudoers", "w") as conf:
        conf.writelines(temp_sudoers)

    print_status("Restoring pacman config")
    with open("/mnt/depthboot/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # comment out CheckSpace
    temp_pacman[34] = temp_pacman[34][1:]
    with open("/mnt/depthboot/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)


# using arch-chroot for arch
def chroot(command: str):
    if verbose:
        bash(f'arch-chroot /mnt/depthboot bash -c "{command}"')
    else:
        bash(f'arch-chroot /mnt/depthboot bash -c "{command}" 2>/dev/null 1>/dev/null')  # supress all output
