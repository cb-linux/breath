# Bootlock

Breath uses an extremely simple mechanism to prevent the system from shutting down when the lid is closed.

When the lid closes or the system is idle for a long time, Linux distributions tend to sleep to S1. This triggers an NVRAM reset and makes you need to boot into an operating system with a signed kernel (only ChromeOS has one). Once you've booted into this OS, you can re-enable USB and unsigned kernel booting.

This is really problematic because sleep / closing the lid doesn't properly work and if ChromeOS has been wiped, you can't re-enable USB and Unsigned kernel booting.

To fix this in the Ubuntu `rootfs` (this has been enabled by default in Breath), the `systemd` config file for power and sleep had to be overriden to sleep to S3. Sleeping to S3 is slightly less power efficient.

Since the sleep mode has been overriden to sleep to S3, the system will stay booted into Ubuntu as long as the boot media is still plugged in. This makes you never need to press `CTRL` `D` to boot; Ubuntu is already booted