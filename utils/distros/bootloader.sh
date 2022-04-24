#!/bin/bash

set -e 

function postinstall {

    # Setup internet for the initial bootstrap
    sudo cp --remove-destination /etc/resolv.conf ${MNT}/etc/resolv.conf

    printq "Installing core packages"

    {
        runChrootCommand "apk update; apk upgrade; apk add xsetroot gnome-icon-theme xdpyinfo inxi dmidecode xf86-video-fbdev xf86-video-intel alpine-conf libx11-dev libxft-dev libxinerama-dev gnome-themes-extra adwaita-icon-theme ttf-dejavu"
        runChrootCommand "setup-xorg-base"
        # Install pygobject and gtk3
        runChrootCommand "apk add python3 py3-gobject3 gtk+3.0-demo"
    } || true

    # At the moment, suspending to ram (mem) doesn't work,
    # depthcharge says "Secure NVRAM (TPM) initialization error"
    # Instead, we can use freeze which doesn't have great power savings,
    # but for the user it functions the same.
    # This is a stopgap solution. Suspend to RAM is the best when working.
    # READ: https://www.kernel.org/doc/html/v4.18/admin-guide/pm/sleep-states.html
    # READ: https://www.freedesktop.org/software/systemd/man/systemd-sleep.conf.html
    # TODO: Find text modification command instead of redirecting echo
    # runChrootCommand "echo 'SuspendState=freeze' >> /etc/systemd/sleep.conf"
    # # Hibernating shouldn't work, but fake it anyways
    # runChrootCommand "echo 'HibernateState=freeze' >> /etc/systemd/sleep.conf"

    # Don't create a new user, we only need root since this is very minimal
    # # Create a new user that isn't root (if they don't exist)
    # if runChrootCommand "id $BREATH_USER"; then
    #   true
    # else
    #   runChrootCommand "useradd -m -G wheel -s /bin/bash $BREATH_USER"
    # fi

    # Remove any root passwords
    runChrootCommand "passwd root -d"

    # Add the user to the sudoers group
    sudo tee -a ${MNT}/etc/sudoers > /dev/null <<EOT
    %wheel ALL=(ALL) ALL
EOT

}
