# Depthcharge

> I am not an expert on Depthcharge. Depthcharge is a very complicated piece of software, of which I only know the surface of. Please excuse any innacurate information.

Depthcharge is a U-boot based bootloader for Chromebooks.

If you want to boot off Depthcharge, you'll want to enable unsigned kernel booting and USB booting from `crossystem`.

ARM Chromebooks need boot media in a seperate format, [documented here](https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices). In the future, this project will support ARM Chromebooks. This is very different from that of x64 Chromebooks.

On x64 Chromebooks, you must:

1. Sign the kernel bzImage and pack the command line with `futility`'s `vbutil-kernel`
2. `dd` it to a small partition on the USB
3. Write the rootfs to a bigger partition

This is really easy, especially compared to building an `.its` file which ARM Chromebooks need.

## Notable missing features

Depthcharge is not a BIOS, nor is it ever meant to be accessed by the end user. As a result, Depthcharge is basically an embedded-systems bootloader.

* No `initramfs` support
    * Makes the Linux boot flow much simpler

## Interesting features

Depthcharge supports Multiboot and ZBI (initramfs support for Fuschia on the Pixelbook Pro). This means that, theoretically, you could boot any Multiboot-spec image, like GRUB2.

However, this requires a recompile of the firmware and you ultimately need to disable Write Protect to flash your new firmware. At that point, a better idea would be using MrChromebox's Tianocore.