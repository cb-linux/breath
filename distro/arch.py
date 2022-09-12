from os import system as bash
import subprocess as sp


def config(de_name: str, distro_version: str) -> None:
    print("\033[96m" + "Configuring Arch" + "\033[0m")
    print("Uncomment arch mirror")
    with open("/mnt/eupnea/etc/pacman.d/mirrorlist", "r") as read:
        mirrors = read.readlines()
    # Uncomment first worldwide mirror
    mirrors[6] = mirrors[6][1:]
    with open("/mnt/eupnea/etc/pacman.d/mirrorlist", "w") as write:
        write.writelines(mirrors)

    print("Applying pacman fixes")
    bash("mount --bind /mnt/eupnea /mnt/eupnea")
    with open("/mnt/eupnea/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # temporarily comment out CheckSpace, coz Pacman fails otherwise
    temp_pacman[34] = f"#{temp_pacman[34]}"
    with open("/mnt/eupnea/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    print("Prepare pacman")
    chroot("pacman-key --init")
    chroot("pacman-key --populate archlinux")
    chroot("pacman -Syy --noconfirm")
    chroot("pacman -Syu --noconfirm")

    print("Installing packages")
    print(chroot("pacman -S --noconfirm base base-devel nano networkmanager xkeyboard-config linux-firmware sudo "
                 "cloud-utils"))
    # linux-firmware is for Wi-Fi
    # cloud-utils is for grow-part

    print("Configuring sudo")
    with open("/mnt/eupnea/etc/sudoers", "r") as conf:
        temp_sudoers = conf.readlines()
    # uncomment wheel group
    temp_sudoers[84] = temp_sudoers[84][2:]
    temp_sudoers[87] = temp_sudoers[87][2:]
    temp_sudoers[90] = temp_sudoers[90][2:]
    with open("/mnt/eupnea/etc/sudoers", "w") as conf:
        conf.writelines(temp_sudoers)

    print("\033[96m" + "Downloading and installing de, might take a while" + "\033[0m")
    match de_name:
        case "gnome":
            print("Installing gnome")
            chroot("pacman -S --noconfirm gnome gnome-extra")
            chroot("systemctl enable gdm.service")
        case "kde":
            print("Installing kde")
            chroot("pacman -S --noconfirm plasma-meta plasma-wayland-session kde-applications")
            chroot("systemctl enable sddm.service")
        case "mate":
            print("Installing mate")
            # no wayland support in mate
            chroot("pacman -S --noconfirm mate mate-extra xorg xorg-server lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "xfce":
            print("Installing xfce")
            # no wayland support in xfce
            chroot("pacman -S --noconfirm xfce4 xfce4-goodies xorg xorg-server lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "lxqt":
            print("Installing lxqt")
            chroot("pacman -S --noconfirm lxqt breeze-icons xorg xorg-server sddm")
            chroot("systemctl enable sddm.service")
        case "deepin":
            print("Installing deepin")
            chroot("pacman -S --noconfirm deepin deepin-kwin deepin-extra xorg xorg-server lightdm")
            # enable deepin specific login
            with open("/mnt/eupnea/etc/lightdm/lightdm.conf", "a") as conf:
                conf.write("greeter-session=lightdm-deepin-greeter")
            chroot("systemctl enable lightdm.service")
        case "budgie":
            print("Installing budgie")
            chroot("pacman -S --noconfirm budgie-desktop budgie-desktop-view budgie-screensaver budgie-control-center "
                   "xorg xorg-server lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "minimal":
            print("Installing xfce")
            # no wayland support in xfce
            chroot("pacman -S --noconfirm xfce4 xorg xorg-server lightdm lightdm-gtk-greeter")
            chroot("systemctl enable lightdm.service")
        case "cli":
            print("Installing nothing")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
    # enable network service
    chroot("systemctl enable NetworkManager.service")
    print("Restoring pacman config")
    with open("/mnt/eupnea/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # comment out CheckSpace
    temp_pacman[34] = temp_pacman[34][1:]
    with open("/mnt/eupnea/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)


# using arch-chroot for arch
def chroot(command: str) -> str:
    return sp.run('arch-chroot /mnt/eupnea bash -c "' + command + '"', shell=True,
                  capture_output=True).stdout.decode("utf-8").strip()


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
