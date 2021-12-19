#!/bin/bash

function postinstall {
    # Setup internet
    sudo cp --remove-destination /etc/resolv.conf /mnt/etc/resolv.conf

    # Add universe to /etc/apt/sources.list so we can install normal packages
    cat > sources.list << EOF
    deb http://us.archive.ubuntu.com/ubuntu  ${DISTRO_CODENAME}          main universe multiverse 
    deb http://us.archive.ubuntu.com/ubuntu  ${DISTRO_CODENAME}-security main universe multiverse 
    deb http://us.archive.ubuntu.com/ubuntu  ${DISTRO_CODENAME}-updates  main universe multiverse
EOF

    sudo cp sources.list /mnt/etc/apt/

    case $DESKTOP in
      cli)
        BASECMD="apt install -y network-manager tasksel software-properties-common"
        ;;

      *)
        BASECMD="apt install -y network-manager lightdm lightdm-gtk-greeter fonts-roboto yaru-theme-icon materia-gtk-theme budgie-wallpapers-focal tasksel software-properties-common; fc-cache"
        ;;
    esac

    # Chroot into the rootfs to install some packages
    sudo mount --bind /dev /mnt/dev
    runChrootCommand "apt update; $BASECMD"
    sudo umount /mnt/dev || sudo umount -lf /mnt/dev
    syncStorage

    if [ $DESKTOP != "cli" ]; then
      # Rice LightDM
      # Use the Materia GTK theme, Yaru Icon theme, and Budgie Wallpapers
      sudo tee -a /mnt/etc/lightdm/lightdm-gtk-greeter.conf > /dev/null <<EOT
      theme-name=Materia
      icon-theme-name=Yaru
      font-name=Roboto
      xft-dpi=120
      background=/usr/share/backgrounds/budgie/blue-surface_by_gurjus_bhasin.jpg
EOT
    fi

    # We need to load the iwlmvm module at startup for WiFi
    sudo sh -c 'echo '\''iwlmvm'\'' >> /mnt/etc/modules'

    # Desktop installation fails without this
    runChrootCommand "apt update -y"

    # Download the desktop that the user has selected
    case $DESKTOP in

      minimal)
        export DESKTOP_PACKAGE="apt install -y xfce4 xfce4-terminal --no-install-recommends"
        ;;

      gnome)
        export DESKTOP_PACKAGE="apt install -y ubuntu-desktop"
        ;;
      
      deepin)
        export DESKTOP_PACKAGE="add-apt-repository ppa:ubuntudde-dev/stable; apt update; apt install -y ubuntudde-dde"
        ;;

      mate)
        export DESKTOP_PACKAGE="apt install -y ubuntu-mate-desktop"
        ;;

      xfce)
        export DESKTOP_PACKAGE="apt install -y xubuntu-desktop"
        ;;

      lxqt)
        export DESKTOP_PACKAGE="apt install -y lubuntu-desktop"
        ;;

      kde)
        export DESKTOP_PACKAGE="apt install -y kde-standard"
        ;;

      openbox)
        # For debugging purposes
        export DESKTOP_PACKAGE="apt install -y openbox xfce4-terminal"
        ;;

      cli)
        export DESKTOP_PACKAGE="echo 'Using CLI, no need to install any desktop packages.'"
        ;;

    esac

    set +e
    runChrootCommand "$DESKTOP_PACKAGE"
    printerr "Ignore libfprint-2-2 fprintd libpam-fprintd errors"

    # GDM3 installs minimal GNOME
    # This makes the default session in LightDM GNOME,
    # instead of whatever the user chose.
    # We can fix this by removing the GNOME session and deleting the shell.
    if [[ $DESKTOP != "gnome" ]]; then
      sudo rm /mnt/usr/share/xsessions/ubuntu.desktop || true
      runChrootCommand "apt remove gnome-shell -y; apt autoremove -y" || true
    fi

    runChrootCommand "apt remove gdm3 pulseaudio"
    printerr "Ignore libfprint-2-2 fprintd libpam-fprintd errors"
    syncStorage
    set -e

    # Only create a new user and add it to the sudo group if the user doesn't already exist
    if runChrootCommand "id $BREATH_USER"; then
      true
    else
      runChrootCommand "adduser $BREATH_USER && usermod -aG sudo $BREATH_USER"
    fi

    # At the moment, suspending to ram (mem) doesn't work,
    # depthcharge says "Secure NVRAM (TPM) initialization error"
    # Instead, we can use freeze which doesn't have great power savings,
    # but for the user it functions the same.
    # This is a stopgap solution. Suspend to RAM is the best when working.
    # READ: https://www.kernel.org/doc/html/v4.18/admin-guide/pm/sleep-states.html
    # READ: https://www.freedesktop.org/software/systemd/man/systemd-sleep.conf.html
    # TODO: Find text modification command instead of redirecting echo
    runChrootCommand "echo 'SuspendState=freeze' >> /etc/systemd/sleep.conf"
    # Hibernating shouldn't work, but fake it anyways
    runChrootCommand "echo 'HibernateState=freeze' >> /etc/systemd/sleep.conf"
}