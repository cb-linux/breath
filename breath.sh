#!/bin/bash

source utils/system.sh # Host OS Abstraction

# Distro and desktop variables from arguments
export DESKTOP=$1
export DISTRO=$2
export DISTRO_VERSION=$3
export MNT="/mnt"
export ORIGINAL_DIR=$(pwd)

# Exit on errors
set -e

# Many much importance
installDependencies toilet

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
printq "NOTE: No UPPERCASE letters, spaces, backslashes, or special characters"
read -r BREATH_USER
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

createBreathUser

printq "Running Breath"
sudo su breath -c "bash setup.sh $1 $2 $3"
