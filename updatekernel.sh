#!/bin/bash

source utils/functions.sh
source utils/extract.sh

export MNT=/mnt

[[ -n "$1" ]] && { export DIR=$1; }

# Ask user which USB Device they would like to use
printq "Which USB Drive or SD Card would you like to use (e.g. /dev/sda)?"
lsblk -o name,model,tran | grep --color=never "usb"
read USB
printq "Ok, using $USB to update the kernel and its modules"

# Mount the USB
sudo mount ${USB}2 /mnt

cd ~/linux-build || { mkdir ~/linux-build; cd ~/linux-build; }

# Set up the kernel.flags depending on the UUID
export USB_ROOTFS=$(sudo blkid -o value -s PARTUUID ${USB}2)
bash <(curl -s https://raw.githubusercontent.com/cb-linux/breath/main/kernel.flags.sh) > kernel.flags

# Download kernel and modules
if [[ -n "$DIR" ]]; then
    echo "Files supplied"
    cp ${DIR}/bzImage.alt bzImage
    cp ${DIR}/modules.alt.tar.xz modules.tar.xz
elif [[ $VERSION == "ALT" ]]; then
    wget https://github.com/cb-linux/breath/releases/latest/download/bzImage.alt -q --show-progress
    ln -s bzImage.alt bzImage
    wget https://github.com/cb-linux/breath/releases/latest/download/modules.alt.tar.xz -q --show-progress
    ln -s modules.alt.tar.xz modules.tar.xz
else
    wget https://github.com/cb-linux/breath/releases/latest/download/bzImage -q --show-progress
    wget https://github.com/cb-linux/breath/releases/latest/download/modules.tar.xz -q --show-progress
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
