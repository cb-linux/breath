#!/bin/bash

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

function installDependencies () {

    # TODO: Implement installDependencies
    # NOTE: Use "$*" to call all function arguments
    
    # Download dependencies based on distribution
    case $DIST in

    Debian)
        # Install dependencies on a Debian host OS
        sudo apt install -y $*
        ;;

    Arch)
        # Install dependencies on a Arch host OS
        # TODO: Implement arch install
        exit
        ;;

    esac

}
