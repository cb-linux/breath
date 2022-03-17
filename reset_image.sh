#!/bin/bash

printf "This will clean out /mnt and delete and /linux-build content.\n"
read -p "Continue? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1

printf "Deleting image and clearing /mnt\n"
sudo rm -Rf /mnt/*
rm -Rf ~/linux-build
