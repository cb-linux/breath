#!/bin/bash

sudo apt install -y cloud-guest-utils fdisk e2fsck-static || true

lsblk | grep -v loop

echo "What is your USB device? (e.g, /dev/sdb)"
echo
read USB

sudo growpart $USB 2
sudo e2fsck -f ${USB}2
sudo resize2fs ${USB}2
