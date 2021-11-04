# Building the Bootlogo

> From a design perspective, it's a pain to design in GIMP. All design work is done in Figma.

Prerequisites: ImageMagick and netpbm installed (`sudo apt install imagemagick netpbm`)

1. Export a PNG from the Geometric Bootsplash in [this Figma Project](https://www.figma.com/file/OnyxfnLTPtkLKayPVwW3jO/Breath-Geometric-Designs?node-id=0%3A1)
2.
        mogrify -format ppm "logo.png"
3. 
        ppmquant 224 logo.ppm > logo_224.ppm
        pnmnoraw logo_224.ppm > logo_final.ppm
4.
        cp ~/Downloads/logo_final.ppm drivers/video/logo/logo_linux_clut224.ppm