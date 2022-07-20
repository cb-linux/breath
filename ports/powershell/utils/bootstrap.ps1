function bootstrapFiles {

	# This doesn't have to do with bootstrapping, but helps later
	# Exit if there are files in /mnt
	if ((ls -A ${MNT})) {
		sudo rm -rf "${MNT}/lost+found"
		#printerr "There are files in ${MNT}! Please clear this directory of any valuable information!"; exit
	}

	# Make our build directory and CD into it
	mkdir -p ~/linux-build
	cd ~/linux-build

	# If the ChromeOS firmware utility doesn't exist, install it and other packages
	printinfo "Installing Dependencies"
	installDependencies vboot-kernel-utils arch-install-scripts git wget cgpt $FW_PACKAGE

	# Download the kernel bzImage and the kernel modules (wget)
	& {
		wget https://github.com/cb-linux/kernel/releases/latest/download/bzImage -O bzImage -q --show-progress
		wget https://github.com/cb-linux/kernel/releases/latest/download/modules.tar.xz -O modules.tar.xz -q --show-progress
		wget https://raw.githubusercontent.com/cb-linux/kernel/main/kernel.flags -O kernel.flags -q --show-progress
	} || true # Wget has the wrong exit status with no clobber

	# READ: Distro dependent step
	# Download the root file system based on the distribution
	switch ($DISTRO) {

		"ubuntu" {
			# Split up the distro version
			# Argument 3 / DISTRO_VERSION should be something like focal-20.04
			if ( !$DISTRO_VERSION ) { printinfo "No Ubuntu version specified, using hirsute-21.04"; export DISTRO_VERSION=hirsute-21.04; }
			export DISTRO_CODENAME=$(echo "$DISTRO_VERSION" | cut -d- -f1) # e.g. hirsute
			export DISTRO_RELEASE=$(echo "$DISTRO_VERSION" | cut -d- -f2)  # e.g. 21.04

			# Download the Ubuntu rootfs if it doesn't exist
			DISTRO_ROOTFS="ubuntu-rootfs.tar.xz"
			wget http://cloud-images.ubuntu.com/releases/${DISTRO_RELEASE}/release/ubuntu-${DISTRO_RELEASE}-server-cloudimg-amd64-root.tar.xz -O $DISTRO_ROOTFS -q --show-progress || & {
				echo "You have supplied an invalid Ubuntu version. It may not be released yet."; exit;
			}
		}

		"arch" {
			# Download the Arch Bootstrap rootfs if it doesn't exist
			DISTRO_ROOTFS="arch-rootfs.tar.gz"
			ARCH_ROOTFS_URL=$(curl -s "http://mirror.rackspace.com/archlinux/iso/latest/" | grep '<li><a href="archlinux-bootstrap-' | grep -v 'sig' | grep --color=never -o -P '(?<=").*(?=")')
			wget "http://mirror.rackspace.com/archlinux/iso/latest/${ARCH_ROOTFS_URL}" -O $DISTRO_ROOTFS -q --show-progress || & {
				echo "The web scraper cannot retrieve the latest Arch Bootstrap version. Rackspace, the mirror for the Arch bootstrap, might be down."; exit;
			}
		}

		"fedora" {
			# Download the Fedora rootfs if it doesn't exist
			# Extracting a Fedora rootfs from koji is quite complicated
			# I've hardcoded it, but otherwise you need to parse a json file
			# TOOD: Implement versioning support in Fedora
			DISTRO_ROOTFS="fedora-rootfs.tar.xz"
			if ( !(Test-Path $DISTRO_ROOTFS) ) {
				wget "https://kojipkgs.fedoraproject.org//packages/Fedora-Container-Base/35/20211127.0/images/Fedora-Container-Base-35-20211127.0.x86_64.tar.xz" -O $DISTRO_ROOTFS -q --show-progress
			}
		}

		"debian" {
			# Debian uses debootstrap rather than extracting a prebuilt rootfs
			installDependencies debootstrap
		}

		"bootloader" {
			# Download the minimal Alpine Linux rootfs
			DISTRO_ROOTFS="alpine-rootfs.tar.xz"
			wget "https://dl-cdn.alpinelinux.org/alpine/v3.15/releases/x86_64/alpine-minirootfs-3.15.0-x86_64.tar.gz" -O $DISTRO_ROOTFS -q --show-progress
		}

		default {
			printerr "Unknown Distribution supplied, only arch, ubuntu, fedora, debian, and bootloader (case-sensitive) are valid distros"
			exit
		}
	}

	# Sign the kernel
	# After this, the kernel can no longer be booted on non-depthcharge devices
	# In powershell, a backtick (`) is used rather than a backslash
	futility vbutil_kernel `
	--arch x86_64 --version 1 `
	--keyblock /usr/share/vboot/devkeys/kernel.keyblock `
	--signprivate /usr/share/vboot/devkeys/kernel_data_key.vbprivk `
	--bootloader kernel.flags `
	--config kernel.flags `
	--vmlinuz bzImage `
	--pack bzImage.signed

}