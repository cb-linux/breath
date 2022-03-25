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

# Install dependencies based on distro
function installDependencies () {

    # NOTE: "$*" is used to call all function arguments

    # Download dependencies based on distribution
    case $DIST in

    Debian)
        # Install dependencies on a Debian host system
        sudo apt install -y $*
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

                    # cgpt
                    cgpt)
                        unset var; # Included in vboot-utils
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
            vboot-kernel-utilities)
                var=vboot-utils;
                ;;

            # cgpt
            cgpt)
               unset var; # Included in vboot-utils
               ;;
        
        esac
        sudo dnf install $* --assumeyes
    done
    ;;

    esac

}
