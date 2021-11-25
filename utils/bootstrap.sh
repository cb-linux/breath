#!/bin/bash

function bootstrapFiles {

  # Make a directory and CD into it
  mkdir -p ~/linux-build
  cd ~/linux-build

  # If the ChromeOS firmware utility doesn't exist, install it and other packages
  printq "Installing Dependencies"
  which futility > /dev/null || sudo apt install -y vboot-kernel-utils arch-install-scripts git wget linux-firmware

  # Download the kernel bzImage and the kernel modules (wget)
  wget https://github.com/MilkyDeveloper/cb-linux/releases/latest/download/bzImage -O bzImage -q --show-progress
  wget https://github.com/MilkyDeveloper/cb-linux/releases/latest/download/modules.tar.xz -O modules.tar.xz -q --show-progress

  # Download the rootfs based on the distribution
  # DISTRO is an environment variable
  case $DISTRO in

  ubuntu)
      # Download the Ubuntu rootfs if it doesn't exist
      DISTRO_ROOTFS="ubuntu-rootfs.tar.xz"
      [[ ! -f $DISTRO_ROOTFS ]] && {
      wget http://cloud-images.ubuntu.com/releases/focal/release/ubuntu-20.04-server-cloudimg-amd64-root.tar.xz -O ubuntu-rootfs.tar.xz -q --show-progress
      }
      ;;

  arch)
      # Download the Arch Bootstrap rootfs if it doesn't exist
      DISTRO_ROOTFS="arch-rootfs.tar.gz"
      [[ ! -f $DISTRO_ROOTFS ]] && {
      wget https://mirror.rackspace.com/archlinux/iso/2021.10.01/archlinux-bootstrap-2021.10.01-x86_64.tar.gz -O arch-rootfs.tar.gz -q --show-progress
      }
      ;;

  *)
      printerr "Unknown Distribution supplied, only arch and ubuntu (case-sensitive) are valid distros"
      exit
      ;;
  esac

  # Write kernel parameters
  wget https://raw.githubusercontent.com/MilkyDeveloper/cb-linux/main/kernel/kernel.flags -O kernel.flags -q --show-progress

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

}