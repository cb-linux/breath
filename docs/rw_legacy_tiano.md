# Building Tianocore for RW_LEGACY

> GRUB2, U-boot, SeaBIOS, and other bootloader from `chromeos-bootimage` are supported

This guide is being performed on a 4-core 8-threads Intel Core i5 8300H, a laptop processor, but with fast internet. Expect speeds to vary based on your hardware.

1. Get Depot Tools working
2. Download ChromiumOS source (`-g minilayout` doesn't work; the main branch is unstable):
   ```
   mkdir -p ~/chromiumos
   cd ~/chromiumos
   repo init -u https://chromium.googlesource.com/chromiumos/manifest -b release-R97-14324.B
   repo sync -j$(nproc) # Downloads sources, typically takes 45 minutes with fast internet
    ```
3. Setup the ChromeOS Chroot:
    ```
    cros_sdk # Takes about 15 minutes
    ```
4. Setup your board:
    ```
    export BOARD=nami # REPLACE YOUR BOARD WITH THIS!
    setup_board --board=${BOARD} # Takes about 45 minutes
    ```
5. Build firmware:
    ```
    export PACKAGE_NAME=chromeos-bootimage
    cros_workon --board=${BOARD} start ${PACKAGE_NAME}
    repo sync -j$(nproc)
    # Takes about 12 minutes:
    time USE="-cb_legacy_tianocore altfw tianocore" emerge-${BOARD} $PACKAGE_NAME
    ```
6. Copy `/build/nami/firmware/tianocore/libpayload.fd` outside of the `cros_sdk` chroot (`/mnt/host`)
7. Package up `UEFIPAYLOAD.fd` into a file flashable into RW_LEGACY.
    ```
    
    ```

start @ 19:35