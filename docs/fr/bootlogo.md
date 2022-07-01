# Compiler le logo de démarrage

> Du point de vue de la conception, il est difficile de concevoir dans GIMP. Tout le travail de conception est effectué dans Figma.

Prérequis: ImageMagick et netpbm installed (`sudo apt install imagemagick netpbm`)

1. Exporter un PNG à partir du Bootsplash géométrique dans [ce projet Figma](https://www.figma.com/file/OnyxfnLTPtkLKayPVwW3jO/Breath-Geometric-Designs?node-id=0%3A1)
2.
        mogrify -format ppm "logo.png"
3. 
        ppmquant 224 logo.ppm > logo_224.ppm
        pnmnoraw logo_224.ppm > logo_final.ppm
4.
        cp ~/Downloads/logo_final.ppm drivers/video/logo/logo_linux_clut224.ppm