<!-- select:start -->
<!-- select-menu-labels: View: -->

#### --Installation Instructions--

<br>

## Supported Devices

**All x64 (non-tablet) Chromebooks released after 2018 are supported.**

However, this project is being developed on `Nami`, so the following models will have audio support:

> ### Is your Chromebook not on the list?
> That's completely fine! As long as it's newer than 2017, chances are that most drivers will already be supported except audio. If you would like audio working, open up a Github Issue with your Chromebook model and post the output of the commands `lsmod` and `find /usr/share/alsa`.

Nami:
* Acer Chromebook 13 / Spin 13
* Dell Inspiron 14 2-in-1 Model 7486 
* Yoga Chromebook C630
* HP Chromebook x360 14 (i3 8130u)
* Acer Chromebook 715
* Acer Chromebook 714
* HP Chromebook 15 G1
* Dell Inspiron Chromebook 14 (7460)

Coral:
* Acer Chromebook 11 (C732, C732T, C732L & C732LT)
* Lenovo 100e Chromebook
* Lenovo 500e Chromebook
* Acer Chromebook 11 (CB311-8H & CB311-8HT)
* Acer Chromebook Spin 11 (CP311-1H & CP311-1HN)
* CTL Chromebook J41
* CTL Chromebook NL7
* CTL Chromebook NL7T-360
* ASUS Chromebook C223
* ASUS Chromebook C423
* ASUS Chromebook C523

Reef:
* Asus Flip C213
* Acer Chromebook Spin 11 R751T

## Running Breath

Due to licensing restraints, you cannot just download an ISO of Breath and flash it. Instead, you *build* the bootable USB.
> Currently, this project can only work on a **full install** of Debian or Ubuntu (**not Crouton or Crostini**). Running this on Arch or Fedora is unsupported.

**Prerequisite:** Git is installed and you have a mainstream, fast USB plugged in

1. `git clone https://github.com/MilkyDeveloper/cb-linux && cd cb-linux`
2. `bash setup.sh cli ubuntu`
(should take ~15 minutes on a 4-core mobile processor)

> * **Using the CLI argument installs a minimal CLI (no desktop!) environment on the USB.** If you would like to install a desktop, you can use `gnome`, `kde`, `minimal`, `deepin`, `xfce`, `lxqt`, `mate` or `openbox` instead of `cli`.
> * You can replace `ubuntu` with `arch` (you can only use `cli`) or `debian` (all desktops are supported)

3. Done! Now just boot into ChromeOS, enter the shell (<kbd>CTRL</kbd> <kbd>ALT</kbd> <kbd>T</kbd>, `shell`), and run:  
`sudo crossystem dev_boot_usb=1; sudo crossystem dev_boot_signed_only=0; sync`  
to enable USB and Custom Kernel Booting.

Reboot, and with the USB plugged in, press <kbd>CTRL</kbd> <kbd>U</kbd> instead of <kbd>CTRL</kbd> <kbd>D</kbd>. After a short black screen, the system should display a login screen.

### Audio

If your device is one of the devices on the above list, you can enable audio.

Once booted into Breath run the command depending on your device's board:

- Nami: `setup-audio`
- Coral: ```SND_CARD=bxtda7219max SND_BOARD=.coral SND_MODULE=snd_soc_sst_bxt_da7219_max98357a setup-audio```
- Reef: ```SND_CARD=bxtda7219max SND_BOARD=.reef.ELECTRO SND_MODULE=snd_soc_sst_bxt_da7219_max98357a setup-audio```

If it is not, that's completely expected! Open up a Github Issue with your Chromebook model and I'll  get audio working.

## Doesn't work? That's expected!

Breath uses the exact ChromeOS Linux kernel. In other words, if the thing not working in Breath works in ChromeOS, it's a toggle away on my side. Just provide details like your **exact** Chromebook model name and your board name (shown on the bottom of the dev mode screen) and make a Github Issue. When you help me add support to your device, chances are 4+ more devices will become supported too!

#### --Project Overview--

[README.md](https://raw.githubusercontent.com/MilkyDeveloper/cb-linux/main/README.md ':include')

<!-- select:end -->