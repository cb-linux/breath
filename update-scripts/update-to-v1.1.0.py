#!/usr/bin/env python3

# This is an old updater script that was in use before the Eupnea Project started hosting their own repos.
# This script only exists to update older v1.0 depthboot devices

import json
import os
import sys
from urllib.request import urlretrieve

from functions import *

# This script will update the postinstall scripts on an existing installation.
if __name__ == "__main__":
    # Restart script as root
    if not os.geteuid() == 0:
        sudo_args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)

    # delete old scripts tmp dir
    rmdir("/tmp/scripts-update")

    # Make new tmp dir
    mkdir("/tmp/scripts-update")

    # delete old scripts
    rmfile("/usr/local/bin/collect-logs")
    rmfile("/usr/local/bin/functions.py")
    rmfile("/usr/local/bin/install-ectool")
    rmfile("/usr/local/bin/install-ectool.py")
    rmfile("/usr/local/bin/install-to-internal")
    rmfile("/usr/local/bin/manage-kernels")
    rmfile("/usr/local/bin/modify-cmdline")
    rmfile("/usr/local/bin/postinstall")
    rmfile("/usr/local/bin/setup-zram")
    rmfile("/usr/local/bin/update-scripts")
    rmfile("/usr/local/bin/setup-audio")

    # Disable old systemd services
    bash("systemctl disable eupnea-postinstall.service")
    bash("systemctl disable eupnea-update.timer")
    bash("systemctl disable eupnea-update.service")
    # Delete old systemd services
    rmfile("/etc/systemd/system/eupnea-postinstall.service")
    rmfile("/etc/systemd/system/eupnea-update.timer")
    rmfile("/etc/systemd/system/eupnea-update.service")

    # Remove scripts versions from eupnea.json
    with open("/etc/eupnea.json", "r") as file:
        eupnea_json = json.load(file)
    del eupnea_json["postinstall_version"]
    del eupnea_json["audio_version"]
    # Write new json to /etc/eupnea.json
    with open("/etc/eupnea.json", "w") as file:
        json.dump(eupnea_json, file)

    # install new scripts via package manager
    match eupnea_json["distro_name"]:
        case "pop-os" | "ubuntu" | "debian":
            mkdir("/usr/local/share/keyrings", create_parents=True)
            # download public key
            urlretrieve(f"https://eupnea-linux.github.io/apt-repo/public.key",
                        filename="/usr/local/share/keyrings/eupnea-utils.key")
            with open("/etc/apt/sources.list.d/eupnea-utils.list", "w") as file:
                file.write("deb [signed-by=/usr/local/share/keyrings/eupnea-utils.key] https://eupnea-linux.github.io/"
                           "apt-repo/debian_ubuntu kinetic main")
            bash("apt-get update -y")
            bash("apt-get install eupnea-utils -y")
        case "fedora":
            bash("sudo dnf config-manager --add-repo https://eupnea-linux.github.io/rpm-repo/eupnea-utils.repo")
            bash("sudo dnf update -y")
            bash("sudo dnf install -y eupnea-utils")
        case "arch":
            pass
        case _:
            print("Unsupported distro")
            exit(1)

    # Download new systemd services
    try:
        bash("git clone --depth=1 https://github.com/eupnea-linux/systemd-services "
             "/tmp/scripts-update/systemd-services")
    except subprocess.CalledProcessError:
        print_error("Couldn't download systemd services. Check your internet connection and try again.")
        exit(1)

    # Install systemd services
    print_status("Installing systemd services")
    # Copy postinstall scripts
    for file in Path("/tmp/scripts-update/systemd-services").iterdir():
        if file.is_file():
            if file.name == "LICENSE" or file.name == "README.md" or file.name == ".gitignore":
                continue  # dont copy license, readme and gitignore
            else:
                cpfile(file.absolute().as_posix(), f"/etc/systemd/system/{file.name}")

    # Enable new systemd services
    bash("systemctl enable eupnea-postinstall.service")
    bash("systemctl enable eupnea-update.timer")
