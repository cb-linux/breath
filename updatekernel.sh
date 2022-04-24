#!/bin/bash

set -e

source utils/functions.sh
source utils/extract.sh

export MNT=/mnt

[[ -n "$1" ]] && { export DIR=$1; }

# Ask user which USB Device they would like to use
printq "Which USB Drive or SD Card would you like to use (e.g. /dev/sda)? All data on the drive will be wiped!"
lsblk -o name,model,tran | grep --color=never "usb"
read USB
printq "Ok, using $USB to update the kernel and its modules"

# Mount the USB
sudo mount ${USB}2 /mnt

cd ~/linux-build || { mkdir ~/linux-build; cd ~/linux-build; }

# Download kernel commandline
wget https://raw.githubusercontent.com/cb-linux/kernel/main/kernel.flags -O kernel.flags -q --show-progress

# Download kernel and modules
if [[ -n "$DIR" ]]; then
    echo "Files supplied"
    cp ${DIR}/bzImage .
    cp ${DIR}/modules.tar.xz .
elif [[ $VERSION == "ALT" ]]; then
    wget https://github.com/cb-linux/breath/releases/latest/download/bzImage.alt -N -q --show-progress
		ln -s bzImage.alt bzImage
    wget https://github.com/cb-linux/breath/releases/latest/download/modules.alt.tar.xz -N -q --show-progress
		ln -s modules.alt.tar.xz modules.tar.xz
else
    wget https://github.com/cb-linux/breath/releases/latest/download/bzImage -N -q --show-progress
    wget https://github.com/cb-linux/breath/releases/latest/download/modules.tar.xz -N -q --show-progress
fi

# Sign the kernel
# After this, the kernel can no longer be booted on non-depthcharge devices
futility vbutil_kernel \
    --arch x86_64 --version 1 \
    --keyblock /usr/share/vboot/devkeys/kernel.keyblock \
    --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk \
    --bootloader kernel.flags \
    --config kernel.flags \
    --vmlinuz bzImage \
    --pack bzImage.signed

# Flash kernel
sudo dd if=bzImage.signed of=${USB}1

# Extract modules
sudo rm -rf ~/linux-build/modules/lib/modules/*
extractModules

# Write Storage
echo "Writing storage..."
sync
