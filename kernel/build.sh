#!/bin/bash

echo "Cloning the kernel repository with --depth 1"
git clone --branch chromeos-4.19 --depth 1 https://chromium.googlesource.com/chromiumos/third_party/kernel.git
cd kernel

echo "Copying and updating kernel config"
cp ../../kernel.conf .config || exit
make olddefconfig

read -p "Would you like to make edits to the kernel config? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    make menuconfig
    cp .config ../../kernel.conf
fi

echo "Building kernel"
make -j$(nproc) || exit
echo "bzImage and modules built"

cp arch/x86/boot/bzImage ../
echo "bzImage created!"

mkdir mod
make -j8 modules_install INSTALL_MOD_PATH=mod

tar cvfJ ../modules.tar.xz mod/lib
echo "modules.tar.xz created!"