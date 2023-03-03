# This script is purely for automatic purposes, it is not meant to be used by end users.

import argparse
from pathlib import Path

import build


def print_header(message: str) -> None:
    print("\033[95m" + message + "\033[0m", flush=True)


def print_error(message: str) -> None:
    print("\033[91m" + message + "\033[0m", flush=True)


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="distro_name", type=str, help="Distro name")
    parser.add_argument(dest="distro_version", type=str, help="Distro version")
    parser.add_argument(dest="de_name", type=str, help="DE name")
    return parser.parse_args()


if __name__ == "__main__":
    args = process_args()
    testing_dict = {
        "distro_name": args.distro_name,
        "distro_version": args.distro_version,
        "de_name": args.de_name,
        "username": "localuser",
        "password": "test",
        "device": "image",
        "kernel_type": "mainline"
    }

    # Start testing
    print_header(f"Testing {args.distro_name} + {args.distro_version} + {args.de_name}")
    try:
        build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                          no_download_progress=True)
        # calculate shrunk image size in gb and round it to 2 decimal places
        image_size = round(Path("./depthboot.img").stat().st_size / 1073741824, 1)
    except Exception as e:
        print_error(str(e))
        print_error(f"Failed to build {args.distro_name} + {args.distro_version} + {args.de_name}")
        image_size = 0
    except SystemExit:
        print_error(f"Unexpected error, retrying: {args.distro_name} + {args.distro_version} + {args.de_name}")
        try:
            build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                              no_download_progress=True)
            # calculate shrunk image size in gb and round it to 2 decimal places
            image_size = round(Path("./depthboot.img").stat().st_size / 1073741824, 1)
        except (Exception, SystemExit) as e:
            print_error(str(e))
            print_error(f"Failed twice to build {args.distro_name} + {args.distro_version} + {args.de_name}")
            image_size = 0

    with open(f"{args.distro_name}-{args.distro_version}-{args.de_name}-results.txt", "w") as f:
        f.write(str(image_size))
