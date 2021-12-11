#!/bin/bash

function postinstall {

    # We are basically doing all the below in order to install NetworkManager :(

    # Setup internet
    sudo cp --remove-destination /etc/resolv.conf /tmp/arch/etc/resolv.conf

    # Fixes pacman
    sudo mount --bind /tmp/arch /tmp/arch

    # We don't need nmtui since Arch has wifi-menu
    # TODO: Add desktop functionality

    # Change the Arch Mirror
    sudo tee -a /tmp/arch/etc/pacman.d/mirrorlist > /dev/null <<EOT
    Server = http://mirror.rackspace.com/archlinux/\$repo/os/\$arch
EOT

    # Generate the Pacman Keys
    sudo arch-chroot /tmp/arch bash -c "pacman-key --init; pacman-key --populate archlinux"

    # Pacstrap /mnt
    sudo mount --bind /mnt /tmp/arch/mnt
    sudo arch-chroot /tmp/arch bash -c "pacstrap /mnt base base-devel nano" # Vim is bad
    sudo umount -f /tmp/arch/mnt || true

    # We're done with our bootstrap arch install in /tmp/arch!
    # NOTE: Use arch-chroot when installed packages, otherwise 

    # Clean up the mess made in /tmp (if possible)
    sudo umount -f /tmp/arch || true
    sudo rm -rf /tmp/arch || true
    
    # Create a new user that isn't root
    if sudo chroot /mnt /bin/bash -c "id $BREATH_USER &>/dev/null"; then
      true
    else
      sudo chroot /mnt /bin/bash -c "useradd -m -G wheel -s /bin/bash $BREATH_USER"
    fi

    # Add the user to the sudoers group
    sudo tee -a /mnt/etc/sudoers > /dev/null <<EOT
    %wheel ALL=(ALL) ALL
EOT

    # Install nmcli for wifi
    sudo arch-chroot /mnt bash -c "pacman -S networkmanager"
}