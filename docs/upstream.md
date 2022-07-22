# Upstream vs. Downstream

> Little information is available on the differences between Upstream and the ChromeOS kernel

* https://www.chromium.org/chromium-os/chromiumos-design-docs/chromium-os-kernel#Modules_and_initrd_98948772996_5484075685963035
    * Swap (`zram`, etc.) unsupported
    * Initramfs is unsupported
* The main difference between Upstream and downstream are drivers. Unfortunately, many drivers aren't upstreamed due to ChromeOS's rapid growth (not to point any fingers at ChromeOS engineers).