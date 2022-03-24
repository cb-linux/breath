#!/bin/bash

function whichOperatingSystem {

    # TODO: Finish work here!

    OS=$(uname -s) # Determine operating system
    
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
    # NOTE: Use "$*" to call all arguments
    exit

}
