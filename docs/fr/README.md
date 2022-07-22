<!-- select:start -->
<!-- select-menu-labels: View: -->

#### --Instructions d'installation--

<br>

> 🎉 Merci à OMGUbuntu ! Pour cette article: https://www.omgubuntu.co.uk/2022/07/i-used-breath-on-my-acer-chromebook-cp713

<br><br>
Nous n'aurions pas pu le faire sans l'aide de la communauté et de tous nos utilisateurs 💖.

## Périphériques compatibles

**Tous les Chromebooks Intel/AMD (x64) 64 bits sont pris en charge**

<details>
<summary>Développer la liste des appareils confirmés pour prendre en charge l'audio</summary>
<br>

> ### Votre Chromebook ne figure pas dans la liste ?
> C'est tout à fait bien ! Tant qu'il est plus récent que 2017, la plupart des pilotes seront déjà pris en charge, sauf l'audio. ** S'il est plus récent que 2019, il est probable que l'audio soit déjà pris en charge **. Si vous souhaitez que l'audio fonctionne, ouvrez une issue Github avec votre modèle de Chromebook et publiez la sortie des commandes `lsmod` et `find /usr/share/alsa`.

**Cartes-mère prises en charge**: `["asuka", "caroline", "cave", "chell", "glados", "kunimitsu", "lars", "sentry" "nami", "octopus", "volteer", "coral", "reef", "hatch", "puff"]`

* IdeaPad Flex 5i Chromebook (13", 5)
* IdeaPad Flex 5i Chromebook
* HP Chromebook x360 14b / HP Chromebook x360 14a
* Acer Chromebook 712
* HP Chromebook 13 G1
* Thinkpad 13 Chromebook
* Chromebook 14 for work (CP5-471)
* ASUS Chromebook Flip C302
* Dell Chromebook 13 3380
* Lenovo Thinkpad 11e Chromebook / Lenovo Thinkpad Yoga 11e Chromebook
* HP Chromebook x360 11 G1 EE
* Samsung Chromebook Pro
* Acer Chromebook  Spin 11 R751T
* Chromebook 15 CB515-1HT/1H
* Acer Chromebook 11 (C732, C732T, C732L & C732LT )
* Lenovo 500e Chromebook
* Lenovo 100e Chromebook
* AcerChromebook 11 (CB311-8H & CB311-8HT)
* Acer Chromebook Spin 11 (CP311-1H & CP311-1HN)
* CTL Chromebook J41
* CTL Chromebook NL7T-360
* CTL Chromebook NL7
* ASUS Chromebook C223
* ASUS Chromebook C423
* ASUS Chromebook C523
* Acer Chromebook 514
* PCmerge Chromebook AL116
* ASUS Chromebook C403
* Acer Chromebook 311
* Acer Chromebook Spin 511
* Lenovo 500e Chromebook 2nd Gen
* Lenovo 100e Chromebook 2nd Gen (Intel)
* Lenovo 300e Chromebook 2nd Gen (Intel)
* Acer Chromebook Spin 512(R851TN)
* Acer Chromebook 512(C851/C851T)
* ASUS-Chromebook-Flip-C214
* ASUS Chromebook Flip C204
* HP Chromebook 11 G7 EE
* HP Chromebook x360 11 G2 EE
* Lenovo Chromebook C340-11
* Lenovo Chromebook S340-14
* Acer Chromebook Spin 311 (CP311-2H)
* Acer Chromebook 314 (CB314-1H/1HT)
* Acer Chromebook 315 (CB315-3H/3HT)
* Acer Chromebook 311 (CB311-9HT/9H) )
* Samsung Chromebook 4
* Samsung Chromebook+
* Samsung Galaxy Chromebook
* ASUS Chromebook Flip C436FA
* HP Chromebook 11 G8 EE
* HP Chromebook x360 11 G3 EE
* HP Chromebook 14 G6
* HP Chromebook 14a
* Acer Chromebook 314 (C933L/LT)
* Ideapad 3 Chromebook
* HP Chromebox G3
* ASUS Chromebox 4
* Acer Chromebox CXI4
* ASUS Fanless Chromebox
* Samsung Galaxy Chromebook 2
* The Acer Chromebook 514 (CB514-1H)
* Acer Chromebook Spin 713 (CP713-3W)
* ASUS Chromebook Flip CX5 (CX5500)
* HP Pro c640 G2 Chromebook
* ASUS Chromebook CX9 (CX9400)
* ASUS Chromebook CX1101
* ASUS Chromebook C424
* Acer Chromebook 515
</details>

## Prise en main de Breath

En raison des restrictions de licence, vous ne pouvez pas simplement télécharger une image ISO de Breath et la flasher. Au lieu de cela, vous *construisez* la clé USB amorçable ou l'ISO.

**Prérequis :** Git est installé et vous disposez d'une carte USB/SD/SDHC grand public rapide de 12 Go ou plus branchée

**Si vous utilisez Crostini :** Suivez d'abord les instructions [ici](https://bugs.chromium.org/p/chromium/issues/detail?id=1303315#c3).

1. ```
    git clone --recurse-submodules https://github.com/cb-linux/breath && cd breath
    ```
2. ```
   FEATURES=ISO,KEYMAP bash setup.sh cli ubuntu
   ```
    Cette commande devrait prendre environ 30 minutes.

    Si vous **ne voulez pas un environnement minimal sans bureau** ou **souhaitez utiliser Crostini**, n'exécutez pas la commande et lisez ci-dessous.

> * Vous devez ajouter `CROSTINI` à `FEATURES` (donc `FEATURES=ISO,KEYMAP,CROSTINI`) si vous exécutez ce script depuis Crostini.

> * **L'utilisation de l'argument CLI installe un environnement CLI minimal (pas de bureau !) sur l'USB.** Si vous souhaitez installer un bureau, vous pouvez utiliser `gnome`, `kde`, `minimal`, `deepin`, `budgie`, `xfce`, `lxqt`, `mate` ou `openbox` au lieu de `cli`.
> * Vous pouvez remplacer `ubuntu` par `arch` (vous ne pouvez utiliser que `cli`) ou `debian` (tous les bureaux sont pris en charge)
> * Ubuntu prend en charge les versions personnalisées. Si vous souhaitez installer Ubuntu 21.10 au lieu de l'Ubuntu 22.04 par défaut, exécutez simplement : `bash setup.sh cli ubuntu impish-21.10`, où `impish` est le nom de code et `21.10` est la version.
> * Vous pouvez supprimer le `FEATURES=ISO` pour utiliser la méthode classique qui écrit directement sur une clé USB.

1. Fait! Flashez le fichier IMG sur une clé USB en utilisant Etcher par exemple.
    - Si vous exécutez depuis Crostini, copiez l'image dans un dossier auquel vous pouvez accéder à partir de l'application Fichiers de ChromeOS, puis modifiez l'extension du fichier ".img" en ".bin".
     - Vous pouvez alors [le flasher](https://www.virtuallypotato.com/burn-an-iso-to-usb-with-the-chromebook-recovery-utility/) à l'aide de l'outil de récupération Chrome.
    - Plus d'informations [ici](https://github.com/cb-linux/breath/issues/186#issuecomment-1120342250)
2. **[RECOMMANDÉ si vous n'êtes pas sur Crostini]** Redimensionnez la partition de votre clé USB en exécutant `bash expand.sh`. Cela étendra votre image USB pour utiliser tout l'espace disponible.
3. Maintenant, démarrez simplement dans ChromeOS, entrez dans le shell (<kbd>CTRL</kbd> <kbd>ALT</kbd> <kbd>T</kbd>, `shell`), et exécutez :
`sudo crossystem dev_boot_usb=1; sudo crossystem dev_boot_signed_only=0; sync`
pour activer le démarrage USB et désactiver la vérification de la signature du noyau.

Redémarrez, et avec l'USB branché, appuyez sur <kbd>CTRL</kbd> <kbd>U</kbd> au lieu de <kbd>CTRL</kbd> <kbd>D</kbd>. Après un court écran noir, le système devrait afficher un écran de connexion.

NetworkManager est installé par défaut sur toutes les distributions. Vous pouvez vous connecter au Wifi en utilisant `nmtui` (pour une interface utilisateur de terminal) ou `nmcli`.

### L'audio

Une fois démarré dans Breath, exécutez la commande en fonction de la carte de votre appareil :

1. Connectez-vous au Wifi sur votre Chromebook ! Vous pouvez utiliser une interface graphique pour cela ou `nmcli`/`nmtui`

2. - Skylake, Kabylake ou Coffeelake (processeur Intel 7e/8e génération) :
      1. `VERSION=ALT bash updatekernel.sh` sur le PC avec lequel vous avez construit Breath (ne peut pas être exécuté depuis Crostini)
      2. `setup-audio` sur votre Chromebook qui a démarré Breath
    - Tous les appareils Apollo Lake (`CORAL` et `REEF`): `apl-sof-setup-audio`
    - Tout le reste : `sof-setup-audio`
      - Ça ne marche pas ? Essayez `SOUNDCARD=rtk sof-setup-audio`
Si l'audio ne fonctionne toujours pas, c'est très bien ! Ouvrez une issue Github avec votre modèle de Chromebook et je ferai fonctionner l'audio.

> #### Avis de non-responsabilité #### Skylake (SKL) / Kabylake (KBL)
>
> Si vous avez un appareil Skylake ou Kabylake, ne modifiez pas les fichiers UCM (`/usr/share/alsa/ucm2/`) pour tenter d'utiliser PulseAudio. Si vous n'avez aucune idée de ce que sont ces éléments, vous pouvez l'ignorer en toute sécurité.
>
> PulseAudio, sans modifications UCM produit des erreurs. Si vous modifiez l'UCM pour supprimer le `Front Mic`, `Rear Mic` et `Mic` (tous ces éléments sont liés à PCM3 sur `da7219max`), PulseAudio et l'audio en général fonctionneront, mais vos haut-parleurs **feront des bruits étranges** ou leurs membranes **éclateront**.

### Quelques informations qui pourraient vous intéresser

**ZRAM:**  
https://github.com/cb-linux/breath/issues/204#issuecomment-1133802766

**Contrôle du ventilateur/ectool :**
https://github.com/cb-linux/breath/issues/168#issuecomment-1142534066

**Test de la prise audio et du micro :**
https://github.com/cb-linux/breath/discussions/190

## Page OpenCollective 

Si vous trouvez cela utile, pensez à faire un don. Comme je ne suis qu'un étudiant, acquérir les ressources pour développer ce projet n'est possible qu'[avec votre soutien 💚](https://opencollective.com/breath)

## Ça ne marche pas ? C'est prévu !

Breath utilise le noyau Linux de ChromeOS. En d'autres termes, si quelque chose ne fonctionne pas dans Breath et fonctionne dans ChromeOS, c'est que le problème vient de Breath. Fournissez simplement des détails tels que le nom de votre modèle **exact** de Chromebook et le nom de votre carte-mère (affichés en bas de l'écran du mode de développement) et créez une issue Github. Lorsque vous m'aidez à ajouter la prise en charge de votre appareil, il y a de fortes chances que quelques autres appareils soient également pris en charge !

#### --Aperçu du projet--

[README.md](https://raw.githubusercontent.com/cb-linux/breath/main/README.md ':include')

<!-- select:end -->
