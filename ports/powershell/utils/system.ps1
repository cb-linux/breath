#!/bin/bash

# Source other files to simplify importing this script on more minimal bash scripts
# (e.g. expand.sh or genimg.sh)
DIR=( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source ${DIR}/functions.sh

# Determine host system 
function whichOperatingSystem {

    $OS=(uname -s)

    # Determine operating system and distro
    if ( $OS == Linux ) {
        
        # Debian
        if (Test-Path /etc/debian_version ) {
            DIST="Debian"
        # Arch
        } elseif (Test-Path /etc/arch-release ) {
            DIST="Arch"
        # Fedora
        } elseif (Test-Path /etc/fedora-release ) {
	        DIST="Fedora"
        }
        # Other
        else {
            printerr "This distribution is not supported, exiting!"
            exit
        }

    } else {
        printerr "$OS is not supported, exiting!"
        exit
    }

}

# Install dependencies based on distro
function installDependencies {

    # NOTE: "$*" is used to call all function arguments

    # Identify the distro if it is undefined
    if ( $null -eq $DIST ) {
        whichOperatingSystem
    }

    echo "Installing $args"

    # Download dependencies based on distribution
    switch ($DIST) {
        "Debian" {
            sudo apt install -y "$args"
        }
        "Arch" {
            if (Test-Path "/usr/bin/yay") {
                # Install dependencies on an Arch host system
                foreach ($package in $args) {
                    # Replace package names relevant to distro
                    switch ($package) {
                        "vboot-kernel-utils" { $package = "vboot-utils" }
                        "cloud-guest-utils" { $package = "growpartfs" }
                        "cgpt" { Clear-Variable package } # Included in vboot-utils
                        Default {}
                    }

                    yay -S --noconfirm $package
                }
            } else {
                # Yay not istalled, exit
                printerr "Please install yay(https://aur.archlinux.org/yay.git) to continue installation, exiting!"
                exit
            }
        }
        "Fedora" {
            # Install dependencies on a Fedora host system
            foreach ($package in $args) {
                # Replace package names relevant to distro
                switch ($package) {
                    "vboot-kernel-utils" { $package = "vboot-utils" }
                    "cloud-guest-utils" { $package = "cloud-utils-growpart" }
                    "cgpt" { Clear-Variable package } # Included in vboot-utils
                    Default {}
                }
                
                sudo dnf install $package --assumeyes
            }
        }
        Default {}
    }
}