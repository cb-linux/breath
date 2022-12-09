#!/usr/bin/env python3

# The update to v1.1.0 is done by the legacy update-scripts script in the postinstall-scripts repo. Therefore, this
# script only needs to update the current depthboot version.

import json
import os
import sys

# This script will update the postinstall scripts on an existing installation.
if __name__ == "__main__":
    # Restart script as root
    if not os.geteuid() == 0:
        sudo_args = ['sudo', sys.executable] + sys.argv + [os.environ]
        os.execlpe('sudo', *sudo_args)

    # Update depthboot version
    with open("/etc/eupnea.json", "r") as file:
        eupnea_json = json.load(file)
    eupnea_json["depthboot_version"] = "v1.1.0"
    # Write new json to /etc/eupnea.json
    with open("/etc/eupnea.json", "w") as file:
        json.dump(eupnea_json, file)
