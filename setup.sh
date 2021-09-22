#!/bin/bash

# Exit if the user did not specify the desktop
[[ ! -z "$1" ]] || { echo "No desktop specified"; exit; }

# Sync Progress Function
function syncStorage {

  echo

  # shellcheck disable=SC2016
  sync & {
    # If the unsynced data (in kB) is greater than 50MB, then show the sync progress
    while [[ $(grep -e Dirty: /proc/meminfo | grep --color=never -o '[0-9]\+') -gt 5000 ]]; do
      SYNC_MB=$(grep -e Dirty: /proc/meminfo | grep --color=never -o '[0-9]\+' | awk '{$1/=1024;printf "%.2fMB\n",$1}')
      echo -en "\r${SYNC_MB}"
      sleep 1
    done
  }

  echo

  #watch -n 1 'grep -e Dirty: /proc/meminfo | grep --color=never -o '\''[0-9]\+'\'' | awk '\''{$1/=1024;printf "%.2fMB\n",$1}'\'''
  #grep -e Dirty: /proc/meminfo | grep --color=never -o '[0-9]\+' | awk '{$1/=1024;printf "%.2fMB\n",$1}'
}

# Distro and desktop variables
DESKTOP=$1
ORIGINAL_DIR=$(pwd)

# Exit on errors
set -e

# Many much importance
which toilet > /dev/null || sudo apt-get install -qq -y toilet

# Show title message - I told you it was important
toilet -f mono12 "Linux"     -F gay
toilet -f mono9  "Installer" -F gay

# Ask for username
echo "What would you like your username to be?"
read -r BREATH_USER

# Make a directory and CD into it
mkdir -p ~/linux-build
cd ~/linux-build

# If the ChromeOS firmware utility doesn't exist, install it and other packages
echo "Installing Dependencies"
which futility > /dev/null || sudo apt install -y vboot-kernel-utils git wget make gcc bison flex libelf-dev

# Download the kernel bzImage and the kernel modules
wget https://github.com/MilkyDeveloper/cb-linux/releases/download/1/bzImage -O bzImage -q --show-progress
[[ ! -f "modules.tar.xz" ]] && {
  wget https://github.com/MilkyDeveloper/cb-linux/releases/download/1/modules.tar.xz -O modules.tar.xz -q --show-progress
}

# Download the Ubuntu rootfs
[[ ! -f "focal.tar.xz" ]] && {
  wget http://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64-root.tar.xz -O focal.tar.xz -q --show-progress
}

# Only do the below if the second stage has not been completed (format/write rootfs to USB)
# For debugging purposes
if [[ $STAGE != 2 ]]; then

# Download kernel parameters
echo "console=tty1 root=/dev/sda2 i915.modeset=1 rootwait rw" > kernel.flags

# Sign the kernel
# After this, the kernel can no longer be booted on non-depthcharge devices
futility --debug vbutil_kernel \
	 --arch x86_64 --version 1 \
	 --keyblock /usr/share/vboot/devkeys/kernel.keyblock \
	 --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk \
	 --bootloader kernel.flags \
	 --config kernel.flags \
	 --vmlinuz bzImage \
	 --pack bzImage.signed

# Check if a USB Drive is plugged in
while true; do
	if [[ -z $(lsblk -o name,model,tran | grep --color=never "usb") ]]; then
		echo "Please plug in a USB Drive (checking again in 5 seconds)"
		sleep 5
	else
		break
	fi
done

# Ask user which USB Device they would like to use
echo "Which USB Drive would you like to use (e.g. /dev/sda)? All data on the drive will be wiped!"
lsblk -o name,model,tran | grep --color=never "usb"
read USB
echo "Ok, using $USB to install Linux"

# Unmount all partitions on the USB and /mnt
# This command will fail, so use set +e
set +e; sudo umount ${USB}*; sudo umount /mnt; set -e

# Format the USB with GPT
# READ: https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices
sudo parted $USB mklabel gpt
echo "Syncing, may take a few minutes"
syncStorage

# Create a 65 Mb kernel partition
# Our kernels are only ~10 Mb though
sudo parted -a optimal $USB unit mib mkpart Kernel 1 65

# Add a root partition
sudo parted -a optimal $USB unit mib mkpart Root 65 100%

# Make depthcharge know that this is a real kernel partition
sudo cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 $USB

# Flash the kernel partition
sudo dd if=bzImage.signed of=${USB}1

# Format the root partition as ext4 and mount it to /mnt
sudo mkfs.ext4 ${USB}2
syncStorage
sudo rm -rf /mnt/*
sudo mount ${USB}2 /mnt

# Extract the Ubuntu rootfs
sudo tar xvpf focal.tar.xz -C /mnt

fi

# Add universe to /etc/apt/sources.list so we can install normal packages
cat > sources.list << EOF
deb http://us.archive.ubuntu.com/ubuntu  focal          main universe multiverse 
deb http://us.archive.ubuntu.com/ubuntu  focal-security main universe multiverse 
deb http://us.archive.ubuntu.com/ubuntu  focal-updates  main universe multiverse
EOF

sudo cp sources.list /mnt/etc/apt/

# Setup internet
sudo cp --remove-destination /etc/resolv.conf /mnt/etc/resolv.conf

# The below method of running commands in a chroot isn't interactive
echo "What would you like the root user's password to be?"
until sudo passwd --root /mnt root; do echo "Retrying Password"; sleep 1; done

# Chroot into the rootfs
sudo mount --bind /dev /mnt/dev
sudo chroot /mnt /bin/bash -x <<'EOF'
apt update
apt install -y network-manager linux-firmware lightdm lightdm-gtk-greeter fonts-roboto yaru-theme-icon materia-gtk-theme budgie-wallpapers-focal tasksel software-properties-common

fc-cache
EOF
sudo umount /mnt/dev || sudo umount -lf /mnt/dev
echo "Syncing, may take a few minutes"
syncStorage

# We need to load the iwlmvm module at startup for WiFi
sudo sh -c 'echo '\''iwlmvm'\'' >> /mnt/etc/modules'

# Rice LightDM
# Use the Materia GTK theme, Yaru Icon theme, and Budgie Wallpapers
sudo tee -a /mnt/etc/lightdm/lightdm-gtk-greeter.conf > /dev/null <<EOT
theme-name=Materia
icon-theme-name=Yaru
font-name=Roboto
xft-dpi=120
background=/usr/share/backgrounds/budgie/blue-surface_by_gurjus_bhasin.jpg
EOT

# Download the desktop that the user has selected
case $DESKTOP in

  minimal)
    export DESKTOP_PACKAGE="apt install -y xfce4 xfce4-terminal --no-install-recommends"
    ;;

  gnome)
    export DESKTOP_PACKAGE="apt install -y ubuntu-desktop"
    ;;

  budgie)
    export DESKTOP_PACKAGE="apt install -y ubuntu-budgie-desktop"
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

  openbox)
    # For debugging purposes
    export DESKTOP_PACKAGE="apt install -y openbox xfce4-terminal"
    ;;

esac

set +e
sudo chroot /mnt /bin/sh -c "$DESKTOP_PACKAGE"
echo "Ignore libfprint-2-2 fprintd libpam-fprintd errors"

# GDM3 installs minimal GNOME
# This makes the default session in LightDM GNOME,
# instead of whatever the user chose.
# We can fix this by removing the GNOME session and deleting the shell.
if [[ $DESKTOP != "gnome" ]]; then
  sudo rm /mnt/usr/share/xsessions/ubuntu.desktop
  sudo chroot /mnt /bin/sh -c "apt remove gnome-shell -y; apt autoremove -y"
fi

sudo chroot /mnt /bin/sh -c "apt remove gdm3 pulseaudio"
echo "Ignore libfprint-2-2 fprintd libpam-fprintd errors"
echo "Syncing, may take a few minutes"
syncStorage
set -e

# Only create a new user and add it to the sudo group if the user doesn't already exist
if sudo chroot /mnt /bin/bash -c "id $BREATH_USER &>/dev/null"; then
  true
else
  sudo chroot /mnt /bin/sh -c "adduser $BREATH_USER && usermod -aG sudo $BREATH_USER"
fi

# Extract the modules to /mnt
sudo mkdir -p /mnt/lib/modules
mkdir -p modules || sudo rm -rf modules; sudo mkdir -p modules
sudo tar xvpf modules.tar.xz -C modules
sudo cp -rv modules/lib/modules/* /mnt/lib/modules
echo "Syncing, may take a few minutes"
syncStorage

# Install all utility files in the bin directory
cd $ORIGINAL_DIR
sudo chmod +x bin/*
sudo cp bin/* /mnt/usr/local/bin
syncStorage

echo "Done!"

# Getting sound working:
# 
# setup-audio