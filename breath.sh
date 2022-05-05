#!/bin/bash

source utils/functions.sh # Functions
source utils/system.sh    # Host OS Abstraction

# Distro and desktop variables from arguments
export DESKTOP=$1
export DISTRO=$2
export DISTRO_VERSION=$3

# Install dependencies
# NOTE: Done in breath.sh without root because some package managers(yay) won't run as root.
printq "Installing Dependencies"
installDependencies toilet vboot-kernel-utils arch-install-scripts git wget cgpt $FW_PACKAGE

# Print 15 lines to "fake" clear the screen
# shellcheck disable=SC2034
for i in {1..15}
do
   echo
done

# Show title message - I told you it was important
toilet -f mono12 -F crop   "Breath"
toilet -f term   -F border "Made by MilkyDeveloper"
echo " $FEATURES"

# Ask for username
printq "What would you like the username to be?"
printq "NOTE: No UPPERCASE letters, spaces, backslashes, or special characters (default: breath)"

read -r BREATH_USER
# If the output is null, set default as breath
if [ -z $BREATH_USER ]; then
    BREATH_USER="breath"
    echo "Using the default username, breath"
fi

export BREATH_USER

# Ask for hostname
printq "\nWhat would you like the hostname to be? (if no hostname is specified, it will be ${DISTRO})"
printq "NOTE: No spaces, backslashes, or special characters"

read -r BREATH_HOST
# If the output is null, use the default hostname
if [ -z $BREATH_HOST ]; then
  BREATH_HOST=$DISTRO
  echo "Using the default hostname, $DISTRO"
fi

export BREATH_HOST

# Create a root user with no password for headless installation called breath
createBreathUser

# Run the breath installer(setup.sh)
sudo -H -u breath bash -c "FEATURES=${FEATURES} bash setup.sh ${DESKTOP} ${DISTRO} ${DISTRO_VERSION} ${BREATH_USER} ${BREATH_HOST}"

# Delete's the breath user, as well as removes any files in /mnt
printq "Cleaning up"
sudo -H -u breath bash -c "sudo rm -rf /mnt/./*" # Run as breath to avoid prompt
sudo mv /etc/sudoers.backup /etc/sudoers
sudo userdel breath
