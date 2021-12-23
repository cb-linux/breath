#!/bin/bash

read -p "What kernel version would you like? (5.4) " KERNEL_VERSION

read -p "Are you satisfied with the current logo? " -n 1 -r
echo

(
    # Bootlogo not working for now
    cd logo
    mogrify -format ppm "logo.png"
    ppmquant 224 logo.ppm > logo_224.ppm
    pnmnoraw logo_224.ppm > logo_final.ppm
)

echo "Cloning kernel $KERNEL_VERSION with --depth 1"
# Latest commit for 5.4: 533e47fa98690d0fe210e0a01777caf96b887a75
git clone --branch chromeos-$KERNEL_VERSION --depth 1 https://chromium.googlesource.com/chromiumos/third_party/kernel.git
cd kernel

echo "Patching the kernel to add logo support"
cp ../logo/logo_final.ppm drivers/video/logo/logo_linux_clut224.ppm
echo "mod" >> .gitignore
touch .scmversion

echo "Copying and updating kernel config"
ls .config || cp ../../kernel.conf .config || exit
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
read -p "Would you like a full rebuild? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    make clean; make -j$(nproc) || exit
else
    make -j$(nproc) || exit
fi
echo "bzImage and modules built"

cp arch/x86/boot/bzImage ../
echo "bzImage created!"

futility --debug vbutil_kernel \
    --arch x86_64 --version 1 \
    --keyblock /usr/share/vboot/devkeys/kernel.keyblock \
    --signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk \
    --bootloader ../kernel.flags \
    --config ../kernel.flags \
    --vmlinuz ../bzImage \
    --pack ../bzImage.signed
echo "Signed bzImage created\!" # Shell expansion weirdness

mkdir mod
make -j8 modules_install INSTALL_MOD_PATH=mod

# Creates an archive containing /lib/modules/...
cd mod
tar cvfJ ../../modules.tar.xz lib/
cd ..
echo "modules.tar.xz created!"

echo "Command to extract modules to USB:"
echo "sudo rm -rf /mnt/lib/modules/* && sudo cp -Rv kernel/mod/lib/modules/* /mnt/lib/modules && sync"
