# Upstream vs. Downstream

> Peu d'informations sont disponibles sur les différences entre Upstream et le noyau ChromeOS

* https://www.chromium.org/chromium-os/chromiumos-design-docs/chromium-os-kernel#Modules_and_initrd_98948772996_5484075685963035
    * Swap (`zram`, etc.) non pris en charge
     * Initramfs n'est pas pris en charge
* La principale différence entre l'upstream et le downstream sont les drivers. Malheureusement, de nombreux drivers ne sont pas en upstream en raison de la croissance rapide de ChromeOS (pour ne pas pointer du doigt les ingénieurs de ChromeOS).