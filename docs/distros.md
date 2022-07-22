# Linux Distributions

You could rip out a `rootfs` from a Linux distro's desktop ISO by extracting a `SquashFS`, but these are not up-to-date, flexible, or uniform. Additionally, they are hardcoded to work with an `initramfs` and have incompatible installers baked-in.

Overall, they have too many quirks to be considering a good solution for a `rootfs`.

Therefore, Breath currently uses minimal cloud root file systems (meant for Docker, etc.). These require minimal postinstall steps.

Although the [Ubuntu postinstall](https://github.com/cb-linux/breath/blob/main/utils/distros/ubuntu.sh) is a whopping 128 lines, most of it is a `switch` statement choosing what command installs what desktop and multiline comments. In reality, all it does is:

* Copy a working `/etc/resolv.conf` from the host
* Add a complete `/etc/apt/sources.list`
* Install NetworkManager for wifi support
* Load the `iwlmvm` module at startup (or create a `udev` rule)
* Install a desktop with a huge `switch` statement
* Create the home user and give a password to the root and home user
* Patch sleep

A new distro should have a bare minimum of:

* Copy a working `/etc/resolv.conf` from the host
* Install NetworkManager for wifi support
* Load the `iwlmvm` module at startup
* Install a desktop with a huge `switch` statement
* Create the home user and give a password to the `root` and home user
* Patch sleep

A great `postinstall` example is in `utils/distros/fedora.sh`

The basic steps of adding a new Linux distro to Breath entail:

* Add an entry to the `switch` statement in `bootstrap.sh` and `extract.sh`
    * [Located here](https://github.com/cb-linux/breath/search?q=%22READ%3A+Distro+dependent+step%22)
* Add a file containing the above postinstall steps to `utils/distros`
    * Name it a one-word name of your distro