#!/bin/bash

set -e

function postinstall {
    
    # Setup internet
    sudo cp --remove-destination /etc/resolv.conf ${MNT}/etc/resolv.conf

    # We're installing the below packages for a cli environment and all desktops
		# xkb-data is needed because currently it gets manually patched for the function keys to work
    BASECMD="apt install -y network-manager tasksel software-properties-common adduser sudo firmware-linux-free firmware-linux-nonfree firmware-iwlwifi iw xkb-data"

    # We need to load the iwlmvm module at startup for WiFi
    sudo tee -a ${MNT}/etc/modules-load.d/modules.conf > /dev/null <<EOT
    iwlmvm
    uvcvideo
    nls_iso8859-1
    nls_cp437
    vfat
EOT

    # we have to add the non-free repository for non-free firmware
    sed -i -e 's/ main/ main contrib non-free/g' ${MNT}/etc/apt/sources.list

    # Download the desktop that the user has selected
    case $DESKTOP in

      minimal)
        export DESKTOP_PACKAGE="apt install -y xfce4 xfce4-terminal --no-install-recommends"
        ;;

      gnome)
        export DESKTOP_PACKAGE="tasksel install desktop gnome-desktop"
        ;;
      
      deepin)
        echo "Deepin is not supported in Ubuntu"; exit
        ;;

      mate)
        export DESKTOP_PACKAGE="apt install -y mate-desktop-environment"
        ;;

      xfce)
        export DESKTOP_PACKAGE="apt install -y task-xfce-desktop"
        ;;

      lxqt)
        export DESKTOP_PACKAGE="apt install -y task-lxqt-desktop"
        ;;

      kde)
        export DESKTOP_PACKAGE="apt install -y task-kde-desktop"
        ;;

      openbox)
        # For debugging purposes
        export DESKTOP_PACKAGE="apt install -y openbox xfce4-terminal"
        ;;

      cli)
        export DESKTOP_PACKAGE="echo 'Using CLI, no need to install any desktop packages.'"
        ;;

    esac

    case $DESKTOP in

      cli)
        SYSTEMD_TARGET="true"
        ;;
      
      *)
        SYSTEMD_TARGET="systemctl set-default graphical.target"
        ;;

    esac

    set +e
    runChrootCommand "apt update -y; $BASECMD; $DESKTOP_PACKAGE; $SYSTEMD_TARGET"
    printerr "Ignore libfprint-2-2 fprintd libpam-fprintd errors"

    runChrootCommand "apt remove -y needrestart"
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
