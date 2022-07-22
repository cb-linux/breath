# Distributions Linux

Vous pouvez extraire un `rootfs` de l'ISO d'une distribution Linux en extrayant un `SquashFS`, mais ceux-ci ne sont pas à jour, flexibles ou uniformes. De plus, ils sont codés en dur pour fonctionner avec un `initramfs` et ont des installateurs incompatibles intégrés.

Dans l'ensemble, ils ont trop de complications pour envisager une bonne solution pour un "rootfs".

Par conséquent, Breath utilise actuellement des images cloud minimales (destinés à Docker, etc.). Celles-ci nécessitent moins d'étapes  après l'installation.

Bien que la [post-installation d'Ubuntu](https://github.com/cb-linux/breath/blob/main/utils/distros/ubuntu.sh) est un fichier de 128 lignes, la plupart étant des `switch` choisissant quelle commande installe quel bureau. En réalité, il ne fait que :

* Copier un `/etc/resolv.conf` fonctionnel à partir de l'hôte
* Ajouter un `/etc/apt/sources.list` complet
* Installer NetworkManager pour le support du wifi
* Charger le module `iwlmvm` au démarrage (ou créer une règle `udev`)
* Installer un bureau
* Créer l'utilisateur courant et attribuer un mot de passe à l'utilisateur `root` et à l'utilisateur courant
* Appliquer un patch pour la mise en veille

Une nouvelle distribution doit avoir un minimum de :

* Copier un `/etc/resolv.conf` fonctionnel à partir de l'hôte
* Installer NetworkManager pour le support du wifi
* Charger le module `iwlmvm` au démarrage
* Installer un bureau 
* Créer l'utilisateur courant et attribuer un mot de passe à l'utilisateur `root` et l'utilisateur courant
* Appliquer un patch pour la mise en veille

Un excellent exemple de `postinstall` se trouve dans `utils/distros/fedora.sh`

The basic steps of adding a new Linux distro to Breath entail:

* Ajoutez une entrée au `switch` dans `bootstrap.sh` et `extract.sh`
    * [Situé ici](https://github.com/cb-linux/breath/search?q=%22READ%3A+Distro+dependent+step%22)
* Ajouter un fichier contenant les étapes de post-installation ci-dessus dans `utils/distros`
    * Nommer-le du même nom que votre distribution