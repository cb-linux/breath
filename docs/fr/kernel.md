## Compilation du noyau

### Prérequis
Les éléments suivants doivent être installés pour réussir à compiler le noyau :
* linux-generic (headers)
* bison (parser, remplacement pour yacc)
* flex (lexical scanner)
* libelf-dev (pour Ubuntu; possiblement libelf-devel or elfutils-libelf-devel pour d'autres distributions)
* imagemagick (fournit la commande mogrify)
* libssl-dev (prend en charge le développement d'openssl)

### Nouveau script de compilation
Dans le dossier du noyau, vous devez exécuter le `build.sh` pour une construction guidée du noyau.

### Manuellement

Des millions de lignes de code ont été versées dans le noyau Linux, ainsi que des milliers de contributions des ingénieurs de Google.

Pour honorer leurs contributions et contribuer à la communauté open-source, ce projet est gratuit et open-source.

Le programme d'installation de ce projet, sur lequel vous êtes actuellement, télécharge 2 éléments au format binaire :

* L'exécutable du noyau Linux (vmlinuz/bzImage)
* Une archive Tar des modules du noyau

Les deux nécessitent un ordinateur puissant et au moins une heure de compilation, ce que de nombreux utilisateurs pour lesquels ce projet est fait n'ont pas. La GPL permet de distribuer des binaires, tant que vous en donnez le code source. La source du noyau et des modules est [ici](https://chromium.googlesource.com/chromiumos/third_party/kernel). Vous pouvez suivre les instructions ci-dessous pour compiler votre propre noyau.

1. Clonez le dépôt avec git en exécutant :
```bash
git clone --branch chromeos-4.19 --depth 1 https://chromium.googlesource.com/chromiumos/third_party/kernel.git
cd kernel
```

2. Téléchargez le fichier `.config` du noyau et mettez-le à jour en exécutant :
```bash
wget https://raw.githubusercontent.com/cb-linux/breath/main/kernel.conf -O .config
make olddefconfig
```

3. Compilez le noyau en exécutant :
```bash
make -j$(nproc)
```

Le `bzImage` doit être situé dans `arch/x86/boot/bzImage`.

Exécuter `make -j$(nproc) modules_install INSTALL_MOD_PATH=[DIRECTORY]`, puis compresser le `[DIRECTORY]` devrait vous donner les modules compressés.
