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

    # Start testing
    print_header("Testing PopOS")
    try:
        build.start_build(verbose=True, local_path=None, dev_release=False, build_options=testing_dict,
                          no_download_progress=True, no_shrink=True)
    except Exception as e:
        print_error(str(e))
        print_error("Failed to build PopOS")
        failed_distros.append("pop-os")

    with open("results.txt", "w") as f:
        f.write(str(failed_distros))
