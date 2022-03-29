#!/bin/bash

# Function for printing a bold, green question or info prompt
function printq {
  echo "$(tput setaf 114; tput bold)$1$(tput sgr0)"
}

# Function for printing a bold, red error
function printerr {
  echo "$(tput setaf 196; tput bold)$1$(tput sgr0)"
}

# Sync Progress Function
function syncStorage {

  printq "Writing storage, may take more than 5 minutes."
  printq "Although it seems slow, consider this process like flashing an ISO to a USB Drive."
  printq "Below is an innacurate indicator of mB left to write. It may decrease hundreds of megabytes in seconds."

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

# Function for waiting for a USB to be plugged in
function waitForUSB {

  USBCOUNTER=1
  while true; do
    if ! lsblk -o name,model,tran | grep -q "usb"; then
      echo -en "\rPlease plug in a USB Drive (Try ${USBCOUNTER}, trying every 5 seconds)"
      sleep 5
      (( USBCOUNTER++ ))
  else
      break
    fi
  done
  echo
  
}

# Function to unmount all partitions on the USB and /mnt
# This command may fail, so use || true
function unmountUSB {
  (sudo umount ${USB}*; sudo umount $MNT; sudo umount /media/*/*) || true
}

# Function for running a command in the chroot
function runChrootCommand {
  sudo chroot $MNT /bin/sh -c "$1"
}

# Function for storing passwd as temporary variable $PASSWD
function getPassword {

    # Define DIST if not defined
    # NOTE: Although this is if statement is being reused from
    # system.sh, in the future if any functions are moved around
    # it will be handy to have this check in both places to prevent
    # silent failure to save passwd.
    if [[ -z $DIST ]]; then
        whichOperatingSystem
    fi

    case $DIST in

        # The yay aur helper cannot be run with sudo priveleges,
        # so instead of reading passwd, we enable '--sudo-loop'.
        Arch)
            yay -Syyu --save --sudoloop --noconfirm
            ;;

        # Every other distro can have $PASSWD silently read
        *)
            read -s -p "[sudo] password for $(whoami): " PASSWD
            ;;
    esac
}
