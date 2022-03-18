#!/bin/bash

# Before we do anything, check if the user is on Crostini,
# since /mnt will already be filled
if [[ $FEATURES == *"CROSTINI"* ]]; then

   mkdir /mnt/breath

fi

# Import
source utils/functions.sh # Functions
source utils/bootstrap.sh # Bootstrap Function
source utils/partition.sh # USB Partitioning
source utils/extract.sh   # Extract Rootfs

# Exit if the user did not specify the desktop
[[ -n "$1" ]] || { printerr "No desktop specified"; exit; }
[[ -n "$2" ]] || { printerr "No distro specified, using Ubuntu"; set -- $1 "ubuntu"; }

# Distro and desktop variables from arguments
export DESKTOP=$1
export DISTRO=$2
export DISTRO_VERSION=$3
export MNT="/mnt"
ORIGINAL_DIR=$(pwd)

# Crostini already has folders in /mnt
if [[ $FEATURES == *"CROSTINI"* ]]; then

   sudo mkdir /mnt/breath
   export MNT="/mnt/breath"

fi

# Import a seperate postinstall function depending on the distro
# shellcheck source=utils/ubuntu_postinstall.sh
source utils/distros/${DISTRO}.sh

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
toilet -f mono12 -F crop   "Breath"
toilet -f term   -F border "Made by MilkyDeveloper"
echo " $FEATURES"

# Ask for username
printq "What would you like your username to be? (no spaces, backslashes, or special characters)"
read -r BREATH_USER
export BREATH_USER

# Bootstrap files
bootstrapFiles

# If the user wants to build an ISO, the partition numbers are different
# (e.g.) /dev/sda2 or /dev/loop9p2 (notice the "p")
if [[ $FEATURES == *"ISO"* ]]; then

   # Create and mount a 6GB IMG File
   echo "Building ISO at ${PWD}/breath.img"
   sleep 10
   fallocate -l 12G breath.img
   export USB=$(sudo losetup -f --show breath.img)
   export USB1="${USB}p1"
   export USB2="${USB}p2"
  
else

   # Wait for a USB to be plugged in
   waitForUSB

   # Ask user which USB Device they would like to use
   printq "Which USB Drive or SD Card would you like to use (e.g. /dev/sda)? All data on the drive will be wiped!"
   lsblk -o name,model,tran | grep --color=never "usb"
   read USB
   printq "Ok, using $USB to install Linux"

   export USB1="${USB}1"
   export USB2="${USB}2"

fi

# Unmount all partitions on the USB and /mnt
unmountUSB

# Partition the USB
partitionUSB

# Our USB has now been fully partitioned
# (1) Write the kernel to a 64mb Partition
# (2) Write a Linux distro rootfs to a partition filling the rest of the storage

# Flash the signed kernel to the kernel partition
sudo dd if=bzImage.signed of=${USB1}

# Format the root partition as ext4 and mount it to /mnt
yes | sudo mkfs.ext4 ${USB2}
syncStorage
sudo umount $MNT || sudo umount -lf $MNT || true
sudo rm -rf ${MNT}/*
sudo mount ${USB2} $MNT

# Extract the rootfs
extractRootfs

# Post-install for specific distros (located in utils/$DISTRO_postinstall.sh)
printq "Running post-installation steps for $DISTRO"
postinstall

# The heredoc (<<EOT) method of running commands in a chroot isn't interactive,
# but luckily passwd has an option to chroot
# In case a user mistypes the password confirmation, retry the password
printq "What would you like the root user's password to be?"
until sudo chroot $MNT sh -c "passwd root"; do printerr "Retrying Password"; sleep 1; done

# Copy (hopefully up-to-date) firmware from the host to the USB
sudo mkdir -p ${MNT}/lib/firmware
sudo cp -Rv /lib/firmware/* ${MNT}/lib/firmware || true
syncStorage

# Extract the modules to /mnt
extractModules

# Install all utility files in the bin directory
cd $ORIGINAL_DIR
sudo chmod 755 bin/*
sudo cp bin/* ${MNT}/usr/local/bin
syncStorage

sudo umount $MNT

set +u

printq "Done!"
if [[ $FEATURES == *"ISO"* ]]; then

   echo "IMG built at ~/linux-build/breath.img"
   echo "You can flash this raw image using Etcher, Rufus, DD, or other ISO flash tools"

fi
echo "Plug the $DISTRO USB with the $DESKTOP desktop into your Chromebook and boot it with CTRL+U"
echo "(Provided that you have enabled USB booting as documented)"

set -u
