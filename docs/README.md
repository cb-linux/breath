<!-- select:start -->
<!-- select-menu-labels: View: -->

#### --Installation Instructions--

<br>

>🎉 Announcement:  
> Crostini support has just been added and [headphone jack/mic support is on the horizon](https://github.com/cb-linux/breath/discussions/190)

## Supported Devices

**All 64-bit Intel/AMD (x64) Chromebooks are supported**

<details>
<summary>Expand List of devices confirmed to support audio</summary>
<br>

> ### Is your Chromebook not on the list?
> That's completely fine! As long as it's newer than 2017, most drivers will already be supported except audio. **If it is newer than 2019, chances are that audio is already supported**. If you would like audio working, open up a Github Issue with your Chromebook model and post the output of the commands `lsmod` and `find /usr/share/alsa`.

**Supported Baseboardboards**: `["nami", "octopus", "volteer", "coral", "reef", "hatch", "puff", "lars", "cave"]`

* IdeaPad Flex 5i Chromebook (13", 5)
* IdeaPad Flex 5i Chromebook
* HP Chromebook x360 14b / HP Chromebook x360 14a
* Acer Chromebook 712
* Chromebook 14 for work (CP5-471)
* ASUS Chromebook Flip C302
* Lenovo Thinkpad 11e Chromebook / Lenovo Thinkpad Yoga 11e Chromebook
* HP Chromebook x360 11 G1 EE
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
* Acer Chromebook 13 / Spin 13
* Dell Inspiron 14 2-in-1 Model 7486
* Yoga Chromebook C630
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
* Lenovo Chromebook C340-15
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

## Running Breath

Due to licensing restraints, you cannot just download an ISO of Breath and flash it. Instead, you *build* the bootable USB or the ISO.

**Prerequisite:** Git is installed and you have a mainstream, fast 12GB or bigger USB/SDCard plugged in

**If you are running Crostini:** Follow the instructions [here](https://bugs.chromium.org/p/chromium/issues/detail?id=1303315#c3) first.

1. ```
    git clone --recurse-submodules https://github.com/cb-linux/breath && cd breath
    ```
2. ```
   FEATURES=ISO,KEYMAP bash setup.sh cli ubuntu
   ```
    This command should take around 30cx minutes.

    If you **don't want a minimal environment without a desktop** or **are running Crostini**, don't run the command and read below.

> * You must add `CROSTINI` to `FEATURES` (so `FEATURES=ISO,KEYMAP,CROSTINI`)  if you're running this script from Crostini.
> * **Using the CLI argument installs a minimal CLI (no desktop!) environment on the USB.** If you would like to install a desktop, you can use `gnome`, `kde`, `minimal`, `deepin`, `budgie`, `xfce`, `lxqt`, `mate` or `openbox` instead of `cli`.
> * You can replace `ubuntu` with `arch` (you can only use `cli`) or `debian` (all desktops are supported)
> * Ubuntu supports custom versions. If you want to install Ubuntu 21.10 instead of the default Ubuntu 22.04, just run: `bash setup.sh cli ubuntu impish-21.10`, where `impish` is the codename and `21.10` is the version.
> * You can remove the `FEATURES=ISO` to use the classic way which directly writes to a USB.

1. Done! Flash the IMG file to a USB using something like Etcher.
    - If you're running this within Crostini, copy it to a folder you can access from ChromeOS's Files App and then change the `.img` file's extension to `.bin`.
    - You can then [flash](https://www.virtuallypotato.com/burn-an-iso-to-usb-with-the-chromebook-recovery-utility/) it by using the Chrome Recovery Tool.
    - More information [here](https://github.com/cb-linux/breath/issues/186#issuecomment-1120342250)
2. **[RECOMMENDED if you are not on Crostini]** Resize the partition of your USB by running `bash expand.sh`. This will expand your USB image to use the entire available space.
3. Now just boot into ChromeOS, enter the shell (<kbd>CTRL</kbd> <kbd>ALT</kbd> <kbd>T</kbd>, `shell`), and run:  
`sudo crossystem dev_boot_usb=1; sudo crossystem dev_boot_signed_only=0; sync`
to enable USB and Custom Kernel Booting.

Reboot, and with the USB plugged in, press <kbd>CTRL</kbd> <kbd>U</kbd> instead of <kbd>CTRL</kbd> <kbd>D</kbd>. After a short black screen, the system should display a login screen.

NetworkManager is installed by default on all distros. You can connect to the Wifi by using `nmtui` (for a terminal user interface) or `nmcli`.

### Audio

Once booted into Breath run the command depending on your device's board:

1. Connect to Wifi on your Chromebook! You can use a GUI for this or `nmcli`/`nmtui`

2. - Skylake, Kabylake, or Coffeelake (7th/8th Gen Intel CPU):
     1. `VERSION=ALT bash updatekernel.sh` on the PC you built Breath with (cannot be run from Crostini)
     2. `setup-audio` on your Chromebook that has booted Breath
   - All Apollo Lake Devices (`CORAL` and `REEF`): `apl-sof-setup-audio`
   - Everything else: `sof-setup-audio`
     - Doesn't work? Try `SOUNDCARD=rtk sof-setup-audio`

If audo still doesn't work, that's completely fine! Open up a Github Issue with your Chromebook model and I'll get audio working.

> #### Skylake (SKL) / Kabylake (KBL) disclaimer
>
> If you have a Skylake or Kabylake device, do not change the UCM files (`/usr/share/alsa/ucm2/`) in an attempt to use PulseAudio. If you have no idea what any of these are, you can safely ignore this.
>
> PulseAudio, without UCM modifications, errors out. If you modify the UCM to remove the `Front Mic`, `Rear Mic`, and `Mic` (all of these are related to PCM3 on `da7219max`), PulseAudio and general audio will work, but your speakers **will be fried** or their membranes **will burst**.

### Goodies

**ZRAM:**  
https://github.com/cb-linux/breath/issues/204#issuecomment-1133802766

**Fan Control/ectool:**  
https://github.com/cb-linux/breath/issues/168#issuecomment-1142534066

**Audio Jack and Mic Testing:**  
https://github.com/cb-linux/breath/discussions/190

## OpenCollective Page

If you find this useful, consider donating. Since I'm only a student, acquiring the resources to expand this project is only possible [with your support 💚](https://opencollective.com/breath)

## Doesn't work? That's expected!

Breath uses the exact ChromeOS Linux kernel. In other words, if the thing not working in Breath works in ChromeOS, it's a toggle away on my side. Just provide details like your **exact** Chromebook model name and your board name (shown on the bottom of the dev mode screen) and make a Github Issue. When you help me add support to your device, chances are a few more devices will become supported too!

#### --Project Overview--

[README.md](https://raw.githubusercontent.com/cb-linux/breath/main/README.md ':include')

<!-- select:end -->
