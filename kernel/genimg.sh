#!/bin/bash

set -e

echo "Building breath.img.gz for installing Breath from Crostini"

# Install kpartx if not found
which kpartx > /dev/null || sudo apt install kpartx -y

export IMG="breath.img"

# Create a blank image file of ~2.6 GB
dd if=/dev/zero of=$IMG bs=512 count=5000000
sync

# GPT Partition it
sudo parted -s $IMG mklabel gpt

# Create partitions
sudo parted -s -a optimal $IMG unit mib mkpart Kernel 1 65
sudo parted -s -a optimal $IMG unit mib mkpart Root 65 100%

# Change the kernel partition type into a ChromeOS kernel
sudo cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 $IMG

# Mount the img
sudo kpartx -av $IMG

# Query the user for the newly made mapper devices
lsblk
ls /dev/mapper
echo "What is the new mapper device? (e.g. /dev/mapper/loop29) "
read MAPPER

# Write the kernel
sudo dd if=bzImage.signed of=${MAPPER}p1

# Format the larger partition to ext4
sudo mkfs.ext4 ${MAPPER}p2

# Write storage
sync

# Unmount mapper devices
sudo kpartx -dv $IMG

# Zip the file into a gz
echo "Gzipping ~1.8 GB img file, will take up to a minute"
gzip breath.img

sync
echo "Done, created breath.img.gz!"