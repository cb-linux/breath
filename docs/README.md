<!-- select:start -->
<!-- select-menu-labels: View: -->

#### --Installation Instructions--

<br>

>🎉 OMGUbuntu article: https://www.omgubuntu.co.uk/2022/07/i-used-breath-on-my-acer-chromebook-cp713
<br><br>
We couldn't have done this without the help of the community and all of our users 💖

## Supported Devices

**All 64-bit Intel/AMD (x64) Chromebooks are supported with a bare-minimum of booting.**

For an exhaustive list of Chromebooks and their CPU Generations, [look here](https://wiki.mrchromebox.tech/Supported_Devices).

### Intel

* Amberlake, Whiskeylake (-UE CPUs), and Skylake
  * All peripherals supported, audio may need extra modules
* Apollolake, Geminilake, Cometlake, Jasperlake, Tigerlake
  * All peripherals supported

### AMD

* Stoneyridge
  * All peripherals supported except audio
  * These Chromebooks are unable to handle Windows on custom UEFI firmware
* Picasso/Dali
  * All peripherals supported except audio, of which I can get running with a tester

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
    This command should take around 30 minutes.

    If you **don't want a minimal environment without a desktop** or **are running Crostini**, don't run the command and read below.

> * You must add `CROSTINI` to `FEATURES` (so `FEATURES=ISO,KEYMAP,CROSTINI`)  if you're running this script from Crostini.
> * **Using the CLI argument installs a minimal CLI (no desktop!) environment on the USB.** If you would like to install a desktop, you can use `gnome`, `kde`, `minimal`, `deepin`, `budgie`, `xfce`, `lxqt`, `mate` or `openbox` instead of `cli`.
> * You can replace `ubuntu` with `arch`, `fedora` (you can only use `cli`) or `debian` (all desktops are supported)
> * Ubuntu supports custom versions. If you want to install Ubuntu 21.10 instead of the default Ubuntu 22.04, just run: `bash setup.sh cli ubuntu impish-21.10`, where `impish` is the codename and `21.10` is the version.
> * Fedora also supports custom versions. Just add the desired version number at the end of `setup.sh` command: `bash setup.sh cli fedora 36`.
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

## OpenCollective Page

If you find this useful, consider donating. Since I'm only a student, acquiring the resources to expand this project is only possible [with your support 💚](https://opencollective.com/breath)

## Goodies

**ZRAM:**  
https://github.com/cb-linux/breath/issues/204#issuecomment-1133802766

**Fan Control/ectool:**  
https://github.com/cb-linux/breath/issues/168#issuecomment-1142534066

**Audio Jack and Mic Testing:**  
https://github.com/cb-linux/breath/discussions/190

## Doesn't work? That's expected!

Breath uses the exact ChromeOS Linux kernel. In other words, if the thing not working in Breath works in ChromeOS, it's a toggle away on my side. Just provide details like your **exact** Chromebook model name and your board name (shown on the bottom of the dev mode screen) and make a Github Issue. When you help me add support to your device, chances are a few more devices will become supported too!

#### --Project Overview--

[README.md](https://raw.githubusercontent.com/cb-linux/breath/main/README.md ':include')

<!-- select:end -->
