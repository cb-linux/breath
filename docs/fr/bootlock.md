# Bootlock

> Bootlock est actuellement bloqué. Cela peut être dû à une régression du noyau ou à un problème de Depthcharge.

Breath utilise un mécanisme extrêmement simple pour empêcher le système de s'arrêter lorsque le couvercle est fermé.

Lorsque le couvercle se ferme ou que le système est inactif pendant une longue période, les distributions Linux ont tendance à se mettre en veille sur S1. Cela déclenche une réinitialisation NVRAM et vous oblige à démarrer dans un système d'exploitation avec un noyau signé (seul ChromeOS en a un). Une fois que vous avez démarré dans ce système d'exploitation, vous pouvez réactiver le démarrage USB et le démarrage du noyau non signé.

C'est vraiment problématique car la mise en veille / la fermeture du couvercle ne fonctionne pas correctement et si ChromeOS a été effacé, vous ne pouvez pas réactiver le démarrage du noyau non signé.

Pour résoudre ce problème dans le `rootfs` d'Ubuntu (ceci a été activé par défaut dans Breath), le fichier de configuration `systemd` pour l'alimentation et la veille a dû être remplacé pour se mettre en veille sur S3. Par ailleurs la mise en veille sur S3 est légèrement moins économe en énergie.

Étant donné que le mode veille a été remplacé par S3, le système restera démarré dans Ubuntu tant que le support de démarrage est toujours branché. Cela vous évite d'avoir à appuyer sur `CTRL` `D` pour démarrer car Ubuntu est déjà démarré.