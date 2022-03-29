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

# Store root passwd in $PASSWD
function getPassword {  
    read -s -p "[sudo] password for $(whoami): " PASSWD
}

# Update system packages
function updateSystemPackages () {

    printq "Updating system packages"

    case $DIST in

        Debian)
            # Update && upgrade packages for debian-based distro's
            read -s $PASSWD || sudo -S apt update --noconfirm && read -s $PASSWD || sudo -S apt upgrade --noconfirm
            ;;

        Arch)
            # Upgrade && update arch-based distro's
            yay -Syy --save --sudoloop --noconfirm
            ;;

        Fedora)
            # Update && upgrade packages for fedora-based distro's
            read -s $PASSWD || sudo -S dnf upgrade --assumeyes
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

    # Cache root passwd for the entirety of the installation
    if [[ -z $PASSWD ]]; then
        getPassword
    fi

    echo "Installing $*"

    # Download dependencies based on distribution
    case $DIST in

    Debian)
        # Install dependencies on a Debian host system
        read -s $PASSWD || sudo -S apt install -y "$@"
        ;; 

    Arch)
        # Install dependencies on a Arch host system
        if [[ -f /usr/bin/yay ]]; then
            # Install dependencies if yay is found
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
                        var=growpartfs;
                        ;;

                    # cgpt
                    cgpt)
                        unset var; # Included in vboot-utils
                        ;;

                esac
                yay -S --save --sudoloop --noconfirm $var
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
                read -s $PASSWD || sudo -S dnf install $var --assumeyes
            fi
        done
        ;;

    esac

}
