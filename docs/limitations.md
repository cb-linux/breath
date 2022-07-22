# Inherent limitations

The ChromeOS kernel has some notable differences. There are probably some major changes in the ChromeOS kernel that are not documented.

## Limitations of current kernels

Sleeping to S1 (standby) is only supported. Suspending to RAM triggers an NVRAM reset and disables all `crossystem` options, including booting an unsigned kernel or from a USB.

## Limitations of outdated kernels

> *The below are limitations of previous kernels. The current kernels used are 5.4 and 5.10, and have none of the below problems*

### TTY and `/dev/fb`

The Framebuffer console and the framebuffer itself (in `/dev/fb0`) do not work in the `chromeos-4.14` and `chromeos-4.19` branches.

### i915 and Mesa

The Mesa version in modern Linux distributions is too old to support the `i915` version in `chromeos-4.4`

### No da7219_max98357a support

`Nami` boards use the *Maxim 98357a* amplifier and *Dialog 7219* codec. These are present on the current kernel used by `Nami` boards, `4.4`, but not in `4.14` or `4.19`. Support recently returned for kernels `5.4` and `5.10`, however.