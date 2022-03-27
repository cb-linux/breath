<br>

# This project's general development has been stalled to focus on audio-related issues

I will no longer be pursuing this whole project for an indefinite amount of time. PulseAudio burnt my speakers on my personal Chromebook once I got it working. My personal laptop's eGPU was already fried because of this project. Therefore, I want to prevent any issues like this before working on the rest if thus project.

In case you also would like to follow my progress on SKL/KBL devices, you can follow the instructions I have documented here:
<br>
<br>
[PulseAudio only working after setting the UCM - kblda7219max on the ChromeOS Kernel, 5.10.70](https://github.com/alsa-project/alsa-ucm-conf/issues/142)

-------------------------------------------

<img src="https://github.com/cb-linux/breath/blob/main/docs/assets/banner.png?raw=true" alt="Breath Banner"></img>

# 🙼 ＢＲＥＡＴＨ

<p align="center">A way to natively run <kbd><img width="25" height="30" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/1200px-Tux.svg.png"></img></kbd> Linux on modern Chromebooks without replacing firmware</p>

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
