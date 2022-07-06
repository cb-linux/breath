#!/bin/bash

function bootstrapFiles {

  # This doesn't have to do with bootstrapping, but helps later
  # Exit if there are files in /mnt
  [ "$(ls -A ${MNT})" ] && {
    sudo rm -rf ${MNT}/lost+found
    "There are files in ${MNT}! Please clear this directory of any valuable information!"; exit
  }

  # Make a directory and CD into it
  mkdir -p ~/linux-build
  cd ~/linux-build

  # If the ChromeOS firmware utility doesn't exist, install it and other packages
  printq "Installing Dependencies"
  installDependencies sudo vboot-kernel-utils arch-install-scripts git parted wget cgpt $FW_PACKAGE

if [[ $FEATURES == *"LOCAL_KERNEL"* ]]; then
  cp $ORIGINAL_DIR/kernel/bzImage .
  cp $ORIGINAL_DIR/kernel/modules.tar.xz .
  cp $ORIGINAL_DIR/kernel/kernel.flags .
  printq "Copied kernel files from breath/kernel"
else
  printq "Downloading kernel files from cb-lines/breath"
  # Download the kernel bzImage and the kernel modules (wget)
  {
  wget https://github.com/cb-linux/breath/releases/latest/download/bzImage -N -q --show-progress
  wget https://github.com/cb-linux/breath/releases/latest/download/modules.tar.xz -N -q --show-progress
  wget https://raw.githubusercontent.com/cb-linux/kernel/main/kernel.flags -N -q --show-progress
  } || true # Wget has the wrong exit status with no clobber
fi

  # READ: Distro dependent step
  # Download the root file system based on the distribution
  case $DISTRO in

  ubuntu)
      # Split up the distro version
      # Argument 3 / DISTRO_VERSION should be something like focal-20.04
      if [[ -n $DISTRO_VERSION ]]; then
        export DISTRO_CODENAME=$(echo "$DISTRO_VERSION" | cut -d- -f1) # e.g. hirsute
        export DISTRO_RELEASE=$(echo "$DISTRO_VERSION" | cut -d- -f2)  # e.g. 21.04
        printq "Using ${DISTRO_CODENAME}-${DISTRO_RELEASE}"
      else
        export DISTRO_CODENAME="jammy" DISTRO_RELEASE="22.04"
        printerr "No Ubuntu version specified, using ${DISTRO_CODENAME}-${DISTRO_RELEASE}"
      fi

      # Download the Ubuntu rootfs if it doesn't exist
      DISTRO_ROOTFS="ubuntu-rootfs.tar.xz"
      wget http://cloud-images.ubuntu.com/releases/${DISTRO_RELEASE}/release/ubuntu-${DISTRO_RELEASE}-server-cloudimg-amd64-root.tar.xz -O $DISTRO_ROOTFS -q --show-progress || {
        echo "You have supplied, or are on, an invalid or unreleased Ubuntu version. Try giving the Ubuntu version as an argument, as mentioned in the docs."; exit;
      }
      ;;

  arch)
      # Download the Arch Bootstrap rootfs if it doesn't exist
      DISTRO_ROOTFS="arch-rootfs.tar.gz"
      #ARCH_ROOTFS_URL=$(curl -s http://mirror.rackspace.com/archlinux/iso/latest/ | grep '<li><a href="archlinux-bootstrap-' | grep -v 'sig' | grep --color=never -o -P '(?<=").*(?=")')
      wget http://mirror.rackspace.com/archlinux/iso/latest/archlinux-bootstrap-x86_64.tar.gz -O $DISTRO_ROOTFS -q --show-progress || {
        echo "The web scraper cannot retrieve the latest Arch Bootstrap version. Rackspace, the mirror for the Arch bootstrap, might be down."; exit;
      }
      ;;

  fedora)
      # Download the Fedora rootfs if it doesn't exist
      # Extracting a Fedora rootfs from koji is quite complicated
      # I've hardcoded it, but otherwise you need to parse a json file
      # TOOD: Implement versioning support in Fedora
      DISTRO_ROOTFS="fedora-rootfs.tar.xz"
      [[ ! -f $DISTRO_ROOTFS ]] && {
      wget "https://kojipkgs.fedoraproject.org//packages/Fedora-Container-Base/35/20211127.0/images/Fedora-Container-Base-35-20211127.0.x86_64.tar.xz" -O $DISTRO_ROOTFS -q --show-progress
      }
      ;;

  debian)
      # Debian uses debootstrap rather than extracting a prebuilt rootfs
      installDependencies debootstrap
      ;;


  bootloader)
      # Download the minimal Alpine Linux rootfs
      DISTRO_ROOTFS="alpine-rootfs.tar.xz"
      wget "https://dl-cdn.alpinelinux.org/alpine/v3.15/releases/x86_64/alpine-minirootfs-3.15.0-x86_64.tar.gz" -O $DISTRO_ROOTFS -q --show-progress
      ;;

  *)
      printerr "Unknown Distribution supplied, only arch, ubuntu, fedora, debian, and bootloader (case-sensitive) are valid distros"
      exit
      ;;
  esac

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
