# ⚠️ Project Archived

> Do not use https://eupnea-linux.github.io/ as an alternative to Breath. There has been shoddy maintenance with no plans forward. Apacelus, the lead maintainer of this, has also started drama with the Chrultrabook server and their superior UEFI solution. There are far more talented individuals working on the correct solution, mainlining, such as WeirdTreeThing who initially worked on Breath's audio and shortly with Apacelus.

Head to [MrChromebox's website](https://mrchromebox.tech/) and have fun with almost full mainline compatibility! This project operated for 2 years as a stopgap and a complete solution until said changes were merged and looked at by kernel developers and AVS was added.

Due to the burden of active maintenance on everything from the boot process to desktop environments, I'm discontinuing this project to work on more engaging projects. The [Discord](https://discord.gg/Hb3GWSEA) will always be open for discussions over Breath and for the enthusiasts that do (or would like to) understand the codebase.

<details>
<summary>View the archived content</summary>
<br>
<img src="https://github.com/cb-linux/breath/blob/main/docs/assets/banner.png?raw=true" alt="Breath Banner"></img>

# 🙼 ＢＲＥＡＴＨ

<p align="center">A way to natively boot and run <kbd><img width="25" height="30" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/1200px-Tux.svg.png"></img></kbd> Linux on modern Chromebooks without replacing firmware</p>

## Supported Devices

**All Chromebooks released after 2017 are supported.**

### Benefits

**Stock Ubuntu:**
* Requires a change in firmware (UEFI or Legacy Boot)
* Has everything working except touchscreen and audio

**Breath:**
* Requires no change in firmware and has all peripherals working on my HP Chromebook 14 x360.

## Running Breath

<h3 align="center"><a href="https://cb-linux.github.io/breath/docs.html#/">📄 Please visit the docs here 📄</a></h3>

## How does everything work?

This project uses the ChromeOS Kernel and firmware. Touchscreen and all other peripherals *just work*. Breath has been carefully designed to not have any legal issues, so you can't flash the ISO or have the audio firmware bundled.

Audio works [perfectly](bin/setup-audio) through ALSA, but not PulseAudio or Pipewire. All apps that use PulseAudio libraries (like Firefox) work as of [this commit](https://github.com/cb-linux/breath/commit/884bd03b8eef554bdbafd7b4d62f36690f472237). You can follow further audio progress [here](https://github.com/cb-linux/breath/projects/1).

**[Looking for Maintainers!]**

</details>
