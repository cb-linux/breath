# Limitations inhérentes

Le noyau ChromeOS présente quelques différences notables. Il y a probablement des changements majeurs dans le noyau ChromeOS qui ne sont pas documentés.

## Limitations des noyaux actuels

La veille sur S1 (veille) est uniquement prise en charge. La suspension de la RAM déclenche une réinitialisation de la NVRAM et désactive toutes les options "crossystem", y compris le démarrage d'un noyau non signé ou à partir d'une clé USB.

## Limitations des noyaux obsolètes

> *Ci-dessous sont les limitations des noyaux précédents. Les noyaux actuellement utilisés sont 5.4 et 5.10, et n'ont aucun des problèmes ci-dessous*

### ATS et `/dev/fb`

La console Framebuffer et le framebuffer lui-même (dans `/dev/fb0`) ne fonctionnent pas dans les branches `chromeos-4.14` et `chromeos-4.19`.

### i915 et Mesa

La version Mesa des distributions Linux modernes est trop ancienne pour prendre en charge la version `i915` dans `chromeos-4.4`

### Pas de prise en charge de da7219_max98357a

Les cartes `Nami` utilisent l'amplificateur *Maxim 98357a* et le codec *Dialog 7219*. Ceux-ci sont présents sur le noyau actuel utilisé par les cartes `Nami`, `4.4`, mais pas dans `4.14` ou `4.19`. Cependant, le support est récemment revenu pour les noyaux `5.4` et `5.10`.