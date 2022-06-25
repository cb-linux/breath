# Depthcharge

> Je ne suis pas un expert en Depthcharge. Depthcharge est un logiciel très compliqué, dont je ne connais que la surface. Veuillez excuser toute information inexacte.

Depthcharge est un chargeur de démarrage basé sur U-boot pour les Chromebooks.

Si vous souhaitez démarrer à partir de Depthcharge, vous devez activer le démarrage du noyau non signé et le démarrage USB à partir de `crossystem`.

Les Chromebooks ARM ont besoin d'un support de démarrage dans un format séparé, [documenté ici](https://wiki.gentoo.org/wiki/Creating_bootable_media_for_depthcharge_based_devices). À l'avenir, ce projet prendra en charge les Chromebooks ARM. Qui sont très différent des Chromebooks x64.

Sur les Chromebooks x64, vous devez :

1.Signez le noyau et emballez la ligne de commande avec le `vbutil-kernel` de `futility`.
2. `dd` vers une petite partition sur l'USB.
3. Écrire le rootfs sur une partition plus grande.

C'est vraiment facile, surtout par rapport à la création d'un fichier ".its" dont les Chromebooks ARM ont besoin.

## Fonctionnalités manquantes notables

Depthcharge n'est pas un BIOS, et il n'est jamais destiné à être accessible par l'utilisateur final. En conséquence, Depthcharge est essentiellement un chargeur de démarrage de systèmes embarqués.

* Pas de prise en charge de `initramfs`
     * Rend le processus de démarrage Linux beaucoup plus simple

## Fonctionnalités intéressantes

Depthcharge prend en charge Multiboot et ZBI (prise en charge d'initramfs pour Fuschia sur le Pixelbook Pro). Cela signifie que, théoriquement, vous pouvez démarrer n'importe quelle image multiboot, comme GRUB2.

Cependant, cela nécessite une recompilation du firmware et vous devez finalement désactiver Write Protect pour flasher votre nouveau firmware. À ce stade, une meilleure idée serait d'utiliser Tianocore de MrChromebox.