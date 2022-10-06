#!/usr/bin/env python3
# This script updates the links in distro.json to point to the latest distro release.
# Currently only needed for fedora

from urllib.request import urlretrieve
import json

if __name__ == '__main__':
    print("\033[96m" + "Starting update script" + "\033[0m")
    with open('distro-links.json', 'r') as file:
        distros_dict = json.load(file)

    print("\033[96m" + "Getting version numbers" + "\033[0m")
    for version in distros_dict["fedora"]:
        print(f"https://kojipkgs.fedoraproject.org/packages/Fedora-Cloud-Base/{version}/")
        urlretrieve(f"https://kojipkgs.fedoraproject.org/packages/Fedora-Cloud-Base/{version}/",
                    f"fedora_link.html")
        with open(f"fedora_link.html", 'r') as file:
            html = file.readlines()
        if version == "Rawhide":
            subversion = html[-4].split('"')[-2][:-1]
        else:
            subversion = html[-3].split('"')[-2][:-1]
        full_link = f"https://kojipkgs.fedoraproject.org/packages/Fedora-Cloud-Base/{version}/{subversion}/images/" \
                    f"Fedora-Cloud-Base-{version}-{subversion}.x86_64.raw.xz"
        distros_dict["fedora"][version] = full_link
        print(f"Fedora version {version} full link: {full_link}")

    print("\033[96m" + "Writing new distro.json" + "\033[0m")
    with open('distro-links.json', 'w') as file:
        json.dump(distros_dict, file, indent=4)
