import json
from pathlib import Path

import build


def print_header(message: str) -> None:
    print("\033[95m" + message + "\033[0m", flush=True)


def print_error(message: str) -> None:
    print("\033[91m" + message + "\033[0m", flush=True)


if __name__ == "__main__":
    print_header("Starting PopOS test")

    testing_dict = {
        "distro_name": "pop-os",
        "distro_version": "22.04",
        "de_name": "cosmic-gnome",
        "username": "localuser",
        "password": "test",
        "device": "image",
        "kernel_type": "mainline"
    }
    failed_distros = []
    size_dict = {}

    # Start testing
    print_header("Testing PopOS")
    try:
        build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                          no_download_progress=True)
        # calculate shrunk image size in gb and round it to 2 decimal places
        size_dict["cosmic-gnome"] = round(Path("./depthboot.img").stat().st_size / 1073741824, 1)
    except Exception as e:
        print_error(str(e))
        print_error("Failed to build PopOS")
        failed_distros.append("pop-os")
        size_dict["cosmic-gnome"] = 0.0
    except SystemExit:
        print_error("Failed to build PopOS, retrying")
        try:
            build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                              no_download_progress=True)
            # calculate shrunk image size in gb and round it to 2 decimal places
            size_dict["cosmic-gnome"] = round(Path("./depthboot.img").stat().st_size / 1073741824, 1)
        except (Exception, SystemExit) as e:
            print_error(str(e))
            print_error("Failed twice to build PopOS")
            failed_distros.append("cosmic-gnome")
            size_dict["cosmic-gnome"] = 0.0

    with open("results_pop-os_22.04.txt", "w") as f:
        f.write(str(failed_distros))

    with open("sizes_pop-os_22.04.json", "w") as file:
        json.dump(size_dict, file)
