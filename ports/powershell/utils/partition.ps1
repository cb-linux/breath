#!/bin/bash

# Function for partitioning the USB
function partitionUSB {

    # It's crucial that we have MNT defined by this stage
    checkMNT

    # Format the USB with GPT
    # READ: https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices
    sudo parted -s $USB mklabel gpt
    syncStorage

    # Create a 65 Mb kernel partition
    # Our kernels are only ~10 Mb though
    sudo parted -s -a optimal $USB unit mib mkpart Kernel 1 65

    # Add a root partition
    sudo parted -s -a optimal $USB unit mib mkpart Root 65 100%

    # Make depthcharge know that this is a real kernel partition
    sudo cgpt add -i 1 -t kernel -S 1 -T 5 -P 15 $USB
    
}