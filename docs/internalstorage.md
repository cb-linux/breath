# Installing to Internal Storage

This will wipe ChromeOS. You can still restore it using a recovery USB. It's recommended to setup your audio (as documented before) and confirm it's working.

1. Find your internal storage disk by running `lsblk`. Chances are this will be `/dev/mmcblk0` or similar. Keep this device name in mind.
   > If you are unable to find your internal storage, run `mount | sed -n 's|^/dev/\(.*\) on / .*|\1|p'` within the ChromeOS Terminal. The ChromeOS Terminal is accessed by typing in CTRL + ALT + T and entering in `shell`
2. Open a terminal and run `install-to-internal-storage` on your Chromebook with the Breath USB booted.