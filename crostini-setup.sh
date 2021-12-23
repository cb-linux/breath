#!/bin/bash

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
ORIGINAL_DIR=$(pwd)

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

# Ask where the USB is mounted
echo "Folders in /mnt/chromeos:"
ls /mnt/chromeos/removable
printq "Where is your USB mounted? (e.g. /mnt/chromeos/removable/'USB Drive') "
read MNT_FOLDER

# Symlink it without spaces
sudo ln -s "$MNT_FOLDER" /mnt/usb
export MNT=/mnt/usb

# Ask for username
printq "What would you like your username to be? (no spaces, backslashes, or special characters)"
read -r BREATH_USER
export BREATH_USER

# Bootstrap files
bootstrapFiles

# Extract the rootfs
extractRootfs

# Post-install for specific distros (located in utils/$DISTRO_postinstall.sh)
postinstall

# The heredoc (<<EOT) method of running commands in a chroot isn't interactive,
# but luckily passwd has an option to chroot
# In case a user mistypes the password confirmation, retry the password
printq "What would you like the root user's password to be?"
until sudo chroot $MNT bash -c "passwd root"; do printerr "Retrying Password"; sleep 1; done

# Copy (hopefully up-to-date) firmware from the host to the USB
sudo mkdir -p ${MNT}/lib/firmware
sudo cp -Rv /lib/firmware/* ${MNT}/lib/firmware || true
syncStorage

# Extract the modules to /mnt
extractModules

# Install all utility files in the bin directory
cd $ORIGINAL_DIR
sudo chmod +x bin/*
sudo cp bin/* ${MNT}/usr/local/bin
syncStorage

sudo umount $MNT
printq "Done!"