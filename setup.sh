#!/bin/bash

# Import
source utils/functions.sh # Functions
source utils/bootstrap.sh # Bootstrap Function
source utils/partition.sh # USB Partitioning
source utils/extract.sh   # Extract Rootfs
source utils/system.sh    # Host OS Abstraction

# Exit if the user did not specify the desktop
[[ -n "$1" ]] || { printerr "No desktop specified"; exit; }
[[ -n "$2" ]] || { printerr "No distro specified, using Ubuntu"; set -- $1 "ubuntu"; }

# Distro and desktop variables from arguments
export DESKTOP=$1
export DISTRO=$2
export DISTRO_VERSION=$3
export MNT="/mnt"
export ORIGINAL_DIR=$(pwd)

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
installDependencies toilet

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

if [[ $FEATURES == *"KEYMAP"* ]]; then
  # Ask to make the Search key a Caps_Lock key
  printq "Do you want to make the Search key a Caps_Lock key ?"
  printq "NOTE: Explicitly yes or no"
  read -r BREATH_CAPSLOCK
  export BREATH_CAPSLOCK
fi

# Ask for username
printq "What would you like the username to be?"
printq "NOTE: No UPPERCASE letters, spaces, backslashes, or special characters"
read -r BREATH_USER
export BREATH_USER

# Ask for hostname
printq "\nWhat would you like the hostname to be? (if no hostname is specified, it will be ${DISTRO})"
printq "NOTE: No spaces, backslashes, or special characters"

read -r BREATH_HOST
# If the output is null, use the default hostname
if [ -z $BREATH_HOST ]; then
  BREATH_HOST=$DISTRO
  echo "Using the default hostname, $DISTRO"
fi

export BREATH_HOST

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
	 if [[ -z "$USB" ]]; then
      echo "ERROR: no loop device"
      exit 1
	 fi
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

# Set the hostname
cat > hostname << EOF
  ${BREATH_HOST}
EOF

sudo cp hostname ${MNT}/etc/

# Install all utility files in the bin directory
cd $ORIGINAL_DIR
sudo chmod 755 bin/*
sudo cp bin/* ${MNT}/usr/local/bin
syncStorage

if [[ $FEATURES == *"KEYMAP"* ]]; then
  # Set keymap
  # Backup the default keymap and copy in the new map
  sudo cp -n ${MNT}/usr/share/X11/xkb/symbols/pc ${MNT}/usr/share/X11/xkb/symbols/pc.org
  sudo cp xkb/xkb.chromebook ${MNT}/usr/share/X11/xkb/symbols/pc

  # Make the Search key a Caps_Lock key, if wanted by the user
  # Backup the default event definitions and copy in the new one
  if [[ $BREATH_CAPSLOCK == "yes" ]]; then
    sudo cp -n ${MNT}/usr/share/X11/xkb/keycodes/evdev ${MNT}/usr/share/X11/xkb/keycodes/evdev.org
    sudo cp xkb/evdev.chromebook ${MNT}/usr/share/X11/xkb/keycodes/evdev
  fi
fi

sudo umount $MNT

set +u
printq "Done!"
if [[ $FEATURES == *"ISO"* ]]; then
   
   sudo losetup -d $USB

   echo "IMG built at ~/linux-build/breath.img"
   echo "You can flash this raw image using Etcher, Rufus, DD, or other ISO flash tools."

fi
echo "Plug the $DISTRO USB with the $DESKTOP desktop into the Chromebook."
echo "Boot with CTRL+U from the OS verification screen."
echo "(Provided that you have enabled USB booting as documented)"
set -u
