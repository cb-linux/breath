#!/bin/bash

# Source other files to simplify importing this script on more minimal bash scripts
# (e.g. expand.sh or genimg.sh)
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
source ${DIR}/functions.sh

# Determines and prepares host system for installation
function whichOperatingSystem {

    # Install os specific package manager if needed
    #NOTE: Scope limited to parent function
    function installPackageManager() (

        # Linux
        if [[ $OS == Linux ]]; then

            # Arch requires yay
            if [[ $DIST == Arch ]]; then

                # Ensure yay is installed
                if ! command -v yay &>/dev/null; then
                    :
                    # Install yay
                    #TODO: figure out root workaround
                    pacman -S --needed git base-devel && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si
                
                fi
            
            fi

        # Darwin requires brew
        elif [[ $OS == Darwin ]]; then

            # Ensure brew is installed
            if ! command -v brew &>/dev/null; then
                #TODO: figure out root workaround
                printq "Installing brew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                brew install coreutils findutils

            fi

        fi

    )

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

    # Darwin(MacOS)
    elif [[ $OS == Darwin ]]; then
        : # Pass the os specific trap below

    else
        printerr "$OS is not supported, exiting!"
        exit
    fi

    # Prepare $OS for the script
    installPackageManager

}

# Check to see if a dependency is already installed
# and skip installation if that is the case.
function checkDependency() {
    
    # NOTE: Distro dependent step
    # NOTE: Debian handles this faster via apt.
    # NOTE: Fedora handles this faster via dnf.

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

    esac

    #TODO: Darwin checkdeps for brew
    
}

# Install dependencies based on distro
function installDependencies () {

    # NOTE: "$*" is used to call all function arguments

    # Linux
    if [[ $OS == Linux ]]; then

        echo "Installing $*"

        # Download dependencies based on distribution
        case $DIST in

        Debian)
            # Install dependencies on a Debian host system
            sudo apt install -y "$@"
            ;;

        Arch)
            # Install dependencies on a Arch host system
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
            ;;

        Fedora)
            # Install dependencies on a Fedora host system
            for var in "$@"
            do
                # Replace package names relevant to distro
                case $var in

                    # vboot-utils
                    vboot-kernel-utils)
                        var=vboot-utils;
                        ;;

                    # growpart
                    cloud-guest-utils)
                        var=cloud-utils-growpart;
                        ;;

                    # cgpt
                    cgpt)
                        unset var; # Included in vboot-utils
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
    
    # Darwin
    elif [[ $OS == Darwin ]]; then
        for var in "$@"
        do
            brew install $var
        done
    
    fi

}

# OS  Abstraction that creates and exports $MNT(breath mountpoint)
function createMountPoint () {
    # Linux
    if [[ $OS == Linux ]]; then
        sudo mkdir /mnt/breath
        export MNT="/mnt/breath"

    elif [[ $OS == Darwin ]]; then
        # sudo mkdir /Volumes/breath
        export MNT="/mnt/breath"
    
    fi

}

# Identify the operating system when this script is sourced
if [[ -z $OS ]]; then
    whichOperatingSystem
fi