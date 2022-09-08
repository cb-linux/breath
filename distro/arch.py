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
    # temporarily comment out CheckSpace, otherwise
    temp_pacman[34] = "#" + temp_pacman[34]
    with open("/mnt/eupnea/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)

    print("Prepare pacman")
    chroot("pacman-key --init; pacman-key --populate archlinux")
    chroot("pacman -Syy --noconfirm")
    chroot("pacman -Syu --noconfirm")

    print("Installing packages")
    chroot("pacman -S --noconfirm base base-devel nano networkmanager xkeyboard-config linux-firmware")
    print("\033[96m" + "Downloading and installing de, might take a while" + "\033[0m")
    '''
    match de_name:
        case "gnome":
            print("Installing gnome")
            chroot("apt install -y ubuntu-desktop")
        case "kde":
            print("Installing kde")
            chroot("apt install -y kde-standard")
        case "mate":
            print("Installing mate")
            chroot("apt install -y ubuntu-mate-desktop")
        case "xfce":
            print("Installing xfce")
            chroot("apt install -y xubuntu-desktop")
        case "lxqt":
            print("Installing lxqt")
            chroot("apt install -y lubuntu-desktop")
        case "deepin":
            print("Installing deepin")
            chroot("add-apt-repository ppa:ubuntudde-dev/stable; apt update; apt install -y ubuntudde-dde")
        case "budgie":
            print("Installing budgie")
            chroot("apt install -y ubuntu-budgie-desktop; sudo dpkg-reconfigure lightdm")
        case "minimal":
            print("Installing minimal")
            chroot("apt install -y xfce4 xfce4-terminal --no-install-recommends")
        case "cli":
            print("Installing nothing")
        case _:
            print("\033[91m" + "Invalid desktop environment!!! Remove all files and retry." + "\033[0m")
    # Ignore libfprint-2-2 fprintd libpam-fprintd errors
    # GDM3 auto installs gnome-minimal. Gotta remove it if user didnt choose gnome
    if not de_name == "gnome":
        print("Fixing gdm3")
        try:
            os.remove("/mnt/eupnea/usr/share/xsessions/ubuntu.desktop")
        except FileNotFoundError:
            pass
        chroot("apt remove -y gnome-shell; apt autoremove -y")
    # TODO: Figure out if this is necessary
    # remove needrestart for some reason?
    chroot("apt remove -y needrestart")
    print("Fixing securetty if needed")
    # "2>/dev/null" is for hiding error message, as not to scare the user
    bash("cp /mnt/eupnea/usr/share/doc/util-linux/examples/securetty /mnt/eupnea/etc/securetty 2>/dev/null")
    '''
    print("Restoring pacman config")
    with open("/mnt/eupnea/etc/pacman.conf", "r") as conf:
        temp_pacman = conf.readlines()
    # comment out CheckSpace
    temp_pacman[34] = temp_pacman[34][1:]
    with open("/mnt/eupnea/etc/pacman.conf", "w") as conf:
        conf.writelines(temp_pacman)


# using arch-chroot for arch
def chroot(command: str) -> str:
    return sp.run('arch-chroot /tmp/eupnea-build/arch bash -c "' + command + '"', shell=True,
                  capture_output=True).stdout.decode("utf-8").strip()


if __name__ == "__main__":
    print("Do not run this file. Use build.py")
