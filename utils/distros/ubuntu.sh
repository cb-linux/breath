#!/bin/bash

function postinstall {
    # Setup internet
    sudo cp --remove-destination /etc/resolv.conf ${MNT}/etc/resolv.conf

    # Determine server based upon build system locale
    TEMP=$(locale | grep LANG=)
    LANG=${TEMP:5:-1}
    printf "\>${LANG}\<\n"

    LOC=${LANG:3:2}
    PREFIX=${LOC,,}
    SOURCE="deb http://${PREFIX}.archive.ubuntu.com/ubuntu ${DISTRO_CODENAME}"
    printq "${SOURCE}"

    # Add universe to /etc/apt/sources.list so we can install normal packages
    cat > sources.list << EOF
    ${SOURCE}          main universe multiverse
    ${SOURCE}-security main universe multiverse
    ${SOURCE}-updates  main universe multiverse
EOF

    sudo cp sources.list ${MNT}/etc/apt/

    BASECMD="apt install -y linux-firmware network-manager tasksel software-properties-common; "
    BASECMD+="apt reinstall -y dbus"

    # Chroot into the rootfs to install some packages
    sudo mount --bind /dev ${MNT}/dev
    runChrootCommand "apt update; $BASECMD"
    sudo umount ${MNT}/dev || sudo umount -lf ${MNT}/dev
    syncStorage

    # We need to load the iwlmvm module at startup for WiFi
    sudo tee -a ${MNT}/etc/modules > /dev/null <<EOT
    iwlmvm
    uvcvideo
    nls_iso8859-1
    nls_cp437
    vfat
EOT

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
    # instead of whatever the user choses.
    # We can fix this by removing the GNOME session and deleting the shell.
    if [[ $DESKTOP != "gnome" ]]; then
      sudo rm ${MNT}/usr/share/xsessions/ubuntu.desktop || true
      runChrootCommand "apt remove gnome-shell -y; apt autoremove -y" || true
    fi

    runChrootCommand "apt remove pulseaudio needrestart" || true
    printerr "Ignore libfprint-2-2 fprintd libpam-fprintd errors"
    syncStorage
    set -e

    # Fix for GDM3
    # https://askubuntu.com/questions/1239503/ubuntu-20-04-and-20-10-etc-securetty-no-such-file-or-directory
    sudo cp ${MNT}/usr/share/doc/util-linux/examples/securetty ${MNT}/etc/securetty

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
