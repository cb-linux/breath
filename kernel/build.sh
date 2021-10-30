#!/bin/bash

read -p "What kernel version would you like?"

echo "Cloning the $REPLY kernel with --depth 1"
git clone --branch chromeos-$REPLY --depth 1 https://chromium.googlesource.com/chromiumos/third_party/kernel.git
cd kernel

echo "Copying and updating kernel config"
cp ../../kernel.conf .config || exit
make olddefconfig

read -p "Would you like to make edits to the kernel config? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    make menuconfig
fi

read -p "Would you like to write the new config to github? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp .config ../../kernel.conf
fi

echo "Building kernel"
make -j$(nproc) || exit
echo "bzImage and modules built"

cp arch/x86/boot/bzImage ../
echo "bzImage created!"

futility --debug vbutil_kernel \
    --arch x86_64 --version 1 \
    --keyblock /usr/share/vboot/devkeys/kernel.keyblock \
    --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk \
    --bootloader kernel.flags \
    --config kernel.flags \
    --vmlinuz bzImage \
    --pack bzImage.signed
echo "Signed bzImage created\!" # Shell expansion weirdness

mkdir mod
make -j8 modules_install INSTALL_MOD_PATH=mod

tar cvfJ ../modules.tar.xz mod/lib
echo "modules.tar.xz created!"

echo "Command to extract modules to USB:"
echo "sudo rm -rf /mnt/lib/modules/*; sudo cp -Rv kernel/mod/lib/modules/* /mnt/lib/modules; sync"