# Installation sur le stockage interne

Cela effacera ChromeOS. Vous pouvez toujours le restaurer à l'aide d'une clé USB de récupération. Il est requis de configurer votre audio avant d'installer sur le stockage interne.

1. Trouvez votre disque de stockage interne en exécutant `lsblk`. Il y a de fortes chances que ce soit `/dev/mmcblk0` ou similaire. Gardez cet appareil en tête.
   > Si vous ne parvenez pas à trouver votre stockage interne, exécutez `mount | sed -n 's|^/dev/\(.*\) on / .*|\1|p'` dans le terminal ChromeOS. Le terminal ChromeOS est accessible en tapant CTRL + ALT + T et en entrant dans `shell`
2. Ouvrez un terminal et exécutez "install-to-internal-storage" sur votre Chromebook depuis Breath afin de l'installer sur votre stockage interne.