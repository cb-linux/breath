#!/bin/bash

# Import
source utils/functions.sh # Functions
source utils/bootstrap.sh # Bootstrap Function
source utils/partition.sh # USB Partitioning
source utils/extract.sh   # Extract Rootfs

# Exit if the user did not specify the desktop
[[ -n "$1" ]] || { printerr "No desktop specified"; exit; }
[[ -n "$2" ]] || { printerr "No distro specified, using Ubuntu"; set -- $1 "ubuntu"; }

# Distro and desktop variables
export DESKTOP=$1
export DISTRO=$2
ORIGINAL_DIR=$(pwd)

# Import a seperate postinstall function depending on the distro
# shellcheck source=utils/ubuntu_postinstall.sh
source utils/${DISTRO}_postinstall.sh

# Exit on errors
set -e

# Many much importance
sudo apt install -y toilet

# Print 15 lines to "fake" clear the screen
# shellcheck disable=SC2034
for i in {1..15}
do
   echo
done

# Show title message - I told you it was important
toilet -f mono12 "Breath" -F gay

# Ask for username
printq "What would you like your username to be? (no spaces, backslashes, or special characters)"
read -r BREATH_USER
export BREATH_USER

# Bootstrap files
bootstrapFiles

# Wait for a USB to be plugged in
waitForUSB

# Ask user which USB Device they would like to use
printq "Which USB Drive would you like to use (e.g. /dev/sda)? All data on the drive will be wiped!"
lsblk -o name,model,tran | grep --color=never "usb"
read USB
printq "Ok, using $USB to install Linux"

# Unmount all partitions on the USB and /mnt
unmountUSB

# Partition the USB
partitionUSB

# Our USB has now been fully partitioned
# (1) We can now write the kernel to a 64mb Partition
# (2) Write a Linux distro rootfs to a partition filling the rest of the storage

# Flash the signed kernel to the kernel partition
sudo dd if=bzImage.signed of=${USB}1

# Format the root partition as ext4 and mount it to /mnt
yes | sudo mkfs.ext4 ${USB}2
syncStorage
sudo umount /mnt || sudo umount -lf /mnt || true
sudo rm -rf /mnt/*
sudo mount ${USB}2 /mnt

# Extract the rootfs
extractRootfs

# Post-install for specific distros (located in utils/$DISTRO_postinstall.sh)
postinstall

# The heredoc (<<EOT) method of running commands in a chroot isn't interactive,
# but luckily passwd has an option to chroot
# In case a user mistypes the password confirmation, retry the password
printq "What would you like the root user's password to be?"
until sudo chroot /mnt bash -c "passwd root"; do printerr "Retrying Password"; sleep 1; done

# Copy (hopefully up-to-date) firmware from the host to the USB
sudo mkdir -p /mnt/lib/firmware
sudo cp -Rv /lib/firmware/* /mnt/lib/firmware
syncStorage

# Extract the modules to /mnt
extractModules

# Install all utility files in the bin directory
cd $ORIGINAL_DIR
sudo chmod +x bin/*
sudo cp bin/* /mnt/usr/local/bin
syncStorage

sudo umount /mnt
printq "Done!"