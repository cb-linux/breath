import json
from pathlib import Path

import build


def print_header(message: str) -> None:
    print("\033[95m" + message + "\033[0m", flush=True)


def print_error(message: str) -> None:
    print("\033[91m" + message + "\033[0m", flush=True)


if __name__ == "__main__":
    print_header("Starting Fedora tests")

    testing_dict = {
        "distro_name": "fedora",
        "distro_version": "37",
        "de_name": "",
        "username": "localuser",
        "password": "test",
        "device": "image",
        "kernel_type": "mainline"
    }
    available_des = ["gnome", "kde", "xfce", "lxqt", "deepin", "budgie", "cli"]
    failed_distros = []
    size_dict = {}

    # Start testing
    for de_name in available_des:
        testing_dict["de_name"] = de_name
        print_header(f"Testing Fedora + {de_name}")
        try:
            build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                              no_download_progress=True)
            # calculate shrunk image size in gb and round it to 2 decimal places
            size_dict[de_name] = round(Path("./depthboot.img").stat().st_size / 1073741824, 1)
        except Exception as e:
            print_error(str(e))
            print_error(f"Failed to build Fedora + {de_name}")
            failed_distros.append(de_name)
            size_dict[de_name] = 0
        except SystemExit:
            print_error(f"Failed to build Fedora + {de_name}, retrying")
            try:
                build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                                  no_download_progress=True)
                # calculate shrunk image size in gb and round it to 2 decimal places
                size_dict[de_name] = round(Path("./depthboot.img").stat().st_size / 1073741824, 1)
            except (Exception, SystemExit) as e:
                print_error(str(e))
                print_error(f"Failed twice to build Fedora + {de_name}")
                failed_distros.append(de_name)
                size_dict[de_name] = 0

    with open("results_fedora_37.txt", "w") as f:
        f.write(str(failed_distros))

    with open("sizes_fedora_37.json", "w") as file:
        json.dump(size_dict, file)
