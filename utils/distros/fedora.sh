#!/bin/bash

function postinstall {

    # Setup internet
    sudo cp --remove-destination /etc/resolv.conf /mnt/etc/resolv.conf

    printq "Installing core packages"
    
    # Install basic packages regardless of desktop (modprobe isn't installed in Fedora container????)
    sudo chroot /mnt /bin/sh -c "dnf group install 'Minimal Install' -y; dnf install NetworkManager-tui ncurses -y"

    # Download the desktop that the user has selected
    case $DESKTOP in

      minimal)
        export DESKTOP_PACKAGE="dnf group install 'Xfce Desktop' -y"
        ;;

      gnome)
        # https://www.reddit.com/r/Fedora/comments/lobnfm/guide_fedora_gnome_minimal_install/
        export DESKTOP_PACKAGE="dnf install @base-x gnome-shell gnome-terminal nautilus firefox chrome-gnome-shell gnome-tweaks @development-tools gnome-terminal-nautilus xdg-user-dirs xdg-user-dirs-gtk gnome-calculator gnome-system-monitor gedit file-roller"
        ;;
      
      deepin)
        export DESKTOP_PACKAGE="dnf group install 'Deepin Desktop' -y"
        ;;

      mate)
        export DESKTOP_PACKAGE="dnf group install 'MATE Desktop' -y"
        ;;

      xfce)
        export DESKTOP_PACKAGE="dnf group install 'Xfce Desktop' -y"
        ;;

      lxqt)
        export DESKTOP_PACKAGE="dnf group install 'LXQt Desktop' -y"
        ;;

      kde)
        export DESKTOP_PACKAGE="dnf group install 'KDE Plasma Workspaces' -y"
        ;;

      openbox)
        # For debugging purposes
        export DESKTOP_PACKAGE="dnf group install 'Basic Desktop' -y"
        ;;

      cli)
        export DESKTOP_PACKAGE="echo 'Using CLI, no need to install any desktop packages.'"
        ;;

    esac

    # Install nonfree repos
    sudo chroot /mnt /bin/bash -c "sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-\$(rpm -E %fedora).noarch.rpm -y"

    # Disable plymouth
    sudo chroot /mnt /bin/sh -c "plymouth-set-default-theme details -R &> /dev/null"

    # Disable zram (swap)
    sudo chroot /mnt /bin/sh -c "dnf remove zram-generator-defaults -y"

    # At the moment, suspending to ram (mem) doesn't work,
    # depthcharge says "Secure NVRAM (TPM) initialization error"
    # Instead, we can use freeze which doesn't have great power savings,
    # but for the user it functions the same.
    # This is a stopgap solution. Suspend to RAM is the best when working.
    # READ: https://www.kernel.org/doc/html/v4.18/admin-guide/pm/sleep-states.html
    # READ: https://www.freedesktop.org/software/systemd/man/systemd-sleep.conf.html
    # TODO: Find text modification command instead of redirecting echo
    sudo chroot /mnt /bin/sh -c "echo 'SuspendState=freeze' >> /etc/systemd/sleep.conf"
    # Hibernating shouldn't work, but fake it anyways
    sudo chroot /mnt /bin/sh -c "echo 'HibernateState=freeze' >> /etc/systemd/sleep.conf"

    # Create a new user that isn't root (if they don't exist)
    if sudo chroot /mnt /bin/bash -c "id $BREATH_USER &>/dev/null"; then
      true
    else
      sudo chroot /mnt /bin/bash -c "useradd -m -G wheel -s /bin/bash $BREATH_USER"
    fi

    # Set a password for the new user
    printq 'Ignore any errors reading "bad password"'
    until sudo chroot /mnt bash -c "passwd $BREATH_USER"; do printerr "Retrying Password"; sleep 1; done

    # Add the user to the sudoers group
    sudo tee -a /mnt/etc/sudoers > /dev/null <<EOT
    %wheel ALL=(ALL) ALL
EOT

}