#!/bin/bash

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

# Install dependencies based on distro
function installDependencies () {

    # TODO: Implement installDependencies
    # NOTE: Use "$*" to call all function arguments
    
    # Download dependencies based on distribution
    case  $DIST in

    Debian)
        # Install dependencies on a Debian host OS
        sudo apt install -y $*
        ;;

    Arch)
        # Install dependencies on a Arch host OS
        if [[ -f /usr/bin/yay ]]; then
            # Install dependencies if yay is found
            yay -S --noconfirm $*

        else
            # Install yay if not on host OS
            printq "Installing yay..."
            git clone https://aur.archlinux.org/yay.git && cd yay
            runUnRootedCommand makepkg -si
            cd .. && rm -rf yay
            yay -Syyu --noconfirm
        fi
        ;;

    esac

}
