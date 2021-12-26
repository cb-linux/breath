<!-- select:start -->
<!-- select-menu-labels: View: -->

#### --Installation Instructions--

<br>

## Supported Devices

**All x64 (non-tablet) Chromebooks released after 2018 are supported.**

However, this project is being developed on `Nami`, so the following models will have audio support:

> ### Is your Chromebook not on the list?
> That's completely fine! As long as it's newer than 2017, chances are that most drivers will already be supported except audio. **If it is newer than 2019, chances are that audio is already supported**. If you would like audio working, open up a Github Issue with your Chromebook model and post the output of the commands `lsmod` and `find /usr/share/alsa`.

Nami:
* Acer Chromebook 13 / Spin 13
* Dell Inspiron 14 2-in-1 Model 7486 
* Yoga Chromebook C630
* HP Chromebook x360 14 (i3 8130u)
* Acer Chromebook 715
* Acer Chromebook 714
* HP Chromebook 15 G1
* Dell Inspiron Chromebook 14 (7460)

Octopus:
* HP Chromebook x360 14b (Blooguard)
* Acer Chromebook 311
* Acer Chromebook Spin 511
* Lenovo 300e Chromebook 2nd Gen (Intel)
* Lenovo 100e Chromebook 2nd Gen (Intel)
* Lenovo 500e Chromebook 2nd Gen
* Acer Chromebook Spin 512 (R851TN)
* Acer Chromebook 512 (C851/C851T)
* ASUS Chromebook Flip C204
* ASUS Chromebook Flip C214
* HP Chromebook x360 11 G2 EE
* HP Chromebook 11 G7 EE
* Lenovo Chromebook C340-11
* Lenovo Chromebook S340-14
* Acer Chromebook 315 (CB315-3H/3HT)
* Acer Chromebook 314 (CB314-1H/1HT)
* Acer Chromebook Spin 311 (CP311-2H)
* Acer Chromebook 311 (CB311-9HT/9H)
* Samsung Chromebook 4
* Samsung Chromebook+
* HP Chromebook x360 11 G3 EE
* HP Chromebook 14 G6
* HP Chromebook 11 G8 EE
* HP Chromebook 14a
* Acer Chromebook 314 (C933L/LT)
* Ideapad 3 Chromebook
* ASUS Chromebook CX1101
* ASUS Chromebook C424

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
- Octopus: `sof-setup-audio`
  - Doesn't work? Try `SOUNDCARD=rtk sof-setup-audio`

If it is not, that's completely expected! Open up a Github Issue with your Chromebook model and I'll  get audio working.

## Doesn't work? That's expected!

Breath uses the exact ChromeOS Linux kernel. In other words, if the thing not working in Breath works in ChromeOS, it's a toggle away on my side. Just provide details like your **exact** Chromebook model name and your board name (shown on the bottom of the dev mode screen) and make a Github Issue. When you help me add support to your device, chances are 4+ more devices will become supported too!

#### --Project Overview--

[README.md](https://raw.githubusercontent.com/MilkyDeveloper/cb-linux/main/README.md ':include')

<!-- select:end -->