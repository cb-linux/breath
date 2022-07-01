# Construire Tianocore pour RW_LEGACY

> GRUB2, U-boot, SeaBIOS et d'autres chargeurs de démarrage de `chromeos-bootimage` sont pris en charge

Ce guide est réalisé sur un processeur Intel Core i5 8300H à 4 cœurs et 8 threads, un processeur pour ordinateur portable, mais avec une connexion Internet rapide. Attendez-vous à ce que les vitesses varient en fonction de votre matériel.

1. Faites fonctionner les outils de dépôt
2. Téléchargez la source de ChromiumOS (`-g minilayout` ne fonctionne pas ; la branche principale est instable) :
   ```
   mkdir -p ~/chromiumos
   cd ~/chromiumos
   repo init -u https://chromium.googlesource.com/chromiumos/manifest -b release-R97-14324.B
   repo sync -j$(nproc) # Télécharge les sources, prend généralement 45 minutes avec une connexion Internet rapide
    ```
3. Configurez le chroot ChromeOS :
    ```
    cros_sdk # Prend environ 15 minutes
    ```
4. Configurez votre carte-mère:
    ```
    export BOARD=nami # REMPLACEZ VOTRE CARTE-MERE PAR ÇA !
    setup_board --board=${BOARD} # Prend environ 45 minutes
    ```
5. Compilez le firmware:
    ```
    export PACKAGE_NAME=chromeos-bootimage
    cros_workon --board=${BOARD} start ${PACKAGE_NAME}
    repo sync -j$(nproc)
    # Prend environ 12 minutes
    time USE="-cb_legacy_tianocore altfw tianocore" emerge-${BOARD} $PACKAGE_NAME
    ```
6. Copiez `/build/nami/firmware/tianocore/libpayload.fd` en dehors du chroot de `cros_sdk` (`/mnt/host`)
7. Emballez `UEFIPAYLOAD.fd` dans un fichier flashable dans RW_LEGACY.
    ```
    
    ```

start @ 19:35