#!/bin/bash

# Source other files to simplify importing this script on more minimal bash scripts
# (e.g. expand.sh or genimg.sh)
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source ${DIR}/functions.sh

# Determine host system 
function whichOperatingSystem {

    OS=$(uname -s)

    # Determine operating system and distro
    if [[ $OS == Linux ]]; then
        
        # Debian
        if [[ -f /etc/debian_version ]]; then
            DIST="Debian"
        
        # Arch
        elif [[ -f /etc/arch-release ]]; then
            DIST="Arch"

	# Fedora
        elif [[ -f /etc/fedora-release ]]; then
	    DIST="Fedora"

        # Other
        else
            printerr "This distribution is not supported, exiting!"
            exit
        fi

    else
        printerr "$OS is not supported, exiting!"
        exit
    fi

}

# Check to see if a dependency is already installed
# and skip installation if that is the case.
function checkDependency() {
    
    # NOTE: Distro dependent step
    # NOTE: Debian handles this faster via apt.

    case $DIST in
        
    Arch)
        if ! command -v pacman -Qi $1 &> /dev/null
        then
            printq "Installing $1..."
            return 1 # Package not present on system
        else
            printq "$1 already installed, skipping..."
            return 0 # Package present on system
        fi
        ;;

    # UNTESTED!
    Fedora)
        if ! command -v dnf list installed $1 &> /dev/null
        then
            printq "Installing $1..."
            return 1 # Package not present on system
        else
            printq "$1 already installed, skipping..."
            return 0 # Package present on system
        fi
        ;;

    esac
    
}

# Install dependencies based on distro
function installDependencies () {

    # NOTE: "$*" is used to call all function arguments

    # Identify the distro if it is undefined
    if [[ -z $DIST ]]; then
        whichOperatingSystem
    fi

    echo "Installing $*"

    # Download dependencies based on distribution
    case $DIST in

    Debian)
        # Install dependencies on a Debian host system
        sudo apt install -y "$@"
        ;;

    Arch)
        # Install dependencies on a Arch host system
        if [[ -f /usr/bin/yay ]]; then
            # Install dependencies if yay is found
            for var in "$@"
            do
                # Replace package names relevant to distro and any packages already installed
                case $var in

                    # vboot-utils
                    vboot-kernel-utils)
                        if checkDependency vboot-utils; then var=""; else var=vboot-utils; fi
                        ;;

                    # growpart
                    cloud-guest-utils)
                        if checkDependency growpartfs; then var=""; else var=growpartfs; fi
                        ;;

                    # cgpt
                    cgpt)
                        unset var; # Included in vboot-utils
                        ;;

                    # Skip any packages already installed that weren't accounted for
                    *)
                        if checkDependency $var; then var=""; else var=$var; fi
                        ;;

                esac
                yay -S --noconfirm $var
            done
        else
            # Yay not istalled, exit
            printerr "Please install yay(https://aur.archlinux.org/yay.git) to continue installation, exiting!"
            exit
        fi
        ;;

    Fedora)
        # Install dependencies on a Fedora host system
        for var in "$@"
        do
            # Replace package names relevant to distro
            case $var in

                # vboot-utils
                vboot-kernel-utils)
                    if checkDependency vboot-utils; then var=""; else var=vboot-utils; fi
                    ;;

                # growpart
                cloud-guest-utils)
                    if checkDependency cloud-utils-growpart; then var=""; else var=cloud-utils-growpart; fi
                    ;;

                # cgpt
                cgpt)
                    unset var; # Included in vboot-utils
                    ;;

                # Skip any packages already installed that weren't accounted for
                *)
                    if checkDependency $var; then var=""; else var=$var; fi
                    ;;
        
            esac
            # dnf doesn't like $FW_PACKAGE, do nothing on null $var
            if [[ -z "$var" ]]; then
                :
            else
                sudo dnf install $var --assumeyes
            fi
        done
        ;;

    esac

}
