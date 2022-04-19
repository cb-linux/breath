# In Powershell, newlines are `n
# Function for printing a bold, green question or info prompt
# Function for printing a bold, red error
function printerr([string]$text) {
    $RED = (tput setaf 196)
    $BOLD = (tput bold)
    $RESET = (tput sgr0)
    $print = "{0}{1}⍰ $text{2}" -f $RED, $BOLD, $RESET
    echo $print
}

# Function for printing a bold, red error
function printinfo([string]$text) {
  $BLUE = (tput setaf 117)
  $BOLD = (tput bold)
  $RESET = (tput sgr0)
  $print = "{0}{1}🛈 $text{2}" -f $BLUE, $BOLD, $RESET
  echo $print
}

# Function for printing a bold, red error
function printerr([string]$text) {
    $RED = (tput setaf 196)
    $BOLD = (tput bold)
    $RESET = (tput sgr0)
    $print = "{0}{1}Ⓧ $text{2}" -f $RED, $BOLD, $RESET
    echo $print
}

# Function for printing for reseting the last line, and then overwriting it
# Not to be confused with Write-Progress
function printProgress([string]$text) {
  /bin/bash -c "echo -en '`r$text'"
}

function getSyncKB {
  return [int] (grep -e Dirty: /proc/meminfo | grep --color=never -o '[0-9]\+')
}

# Helper function for syncStorage
function printSyncProgress {
  $INITIAL_SYNC_NUMBER=getSyncKB

  # If the unsynced data (in kB) is greater than 50MB, then show the sync progress
  while ( getSyncKB -gt 5000 ) {
    $SYNC_KB_NUMBER=getSyncKB
    if ($SYNC_KB_NUMBER -gt $INITIAL_SYNC_NUMBER) { $INITIAL_SYNC_NUMBER=$SYNC_KB_NUMBER }
    #echo "`r$SYNC_MB"
    $SYNC_MB="{0}MB" -f ($SYNC_KB_NUMBER/1024)
    $SYNC_PERCENT=((1-($SYNC_KB_NUMBER/$INITIAL_SYNC_NUMBER))*100)
    Write-Progress -Activity "Writing Storage" -Status "$SYNC_MB left to write" -PercentComplete $SYNC_PERCENT
    sleep 1
  }
}

# Sync Progress Function
function syncStorage {

    printq "Writing storage, may take more than 5 minutes."
    printq "Although it seems slow, consider this process like flashing an ISO to a USB Drive."
    printq "Below is an innacurate indicator of mB left to write. It may decrease hundreds of megabytes in seconds."

    # shellcheck disable=SC2016
    sync & printSyncProgress

    echo "`n"

    #watch -n 1 'grep -e Dirty: /proc/meminfo | grep --color=never -o '\''[0-9]\+'\'' | awk '\''{$1/=1024;printf "%.2fMB\n",$1}'\'''
    #grep -e Dirty: /proc/meminfo | grep --color=never -o '[0-9]\+' | awk '{$1/=1024;printf "%.2fMB\n",$1}'
}

# Function for waiting for a USB to be plugged in
function waitForUSB {

  $USBCOUNTER=1
  while($true) {
    # If there is a USB device plugged in
    if ([string]::IsNullOrWhitespace($(lsblk -o name,model,tran | grep "usb"))) {
      printProgress "Please plug in a USB Drive (Try ${USBCOUNTER}, trying every 5 seconds)"
      sleep 5
      ++$USBCOUNTER
    } else {
      break
    }
  }
  echo "`n"
}

# Function to unmount all partitions on the USB and /mnt
# This command may fail, so use & {}
function unmountUSB {
  & {sudo umount ${USB}*; sudo umount $MNT; sudo umount /media/*/*} || printinfo "USBs are already unmounted"
}

# Function for running a command in the chroot
function runChrootCommand([string]$text) {
  sudo chroot $MNT /bin/sh -c "$text"
}