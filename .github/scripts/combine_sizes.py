import contextlib
import json
import glob

if __name__ == "__main__":
    # open the sizes files in each result's directory
    files = glob.glob("./results_*/*_results.txt")
    all_sizes = {}
    for file in files:
        with open(file, "r") as f:
            data = f.read()
        distro_name = file.split("/")[2].split("_")[0]
        distro_version = file.split("/")[2].split("_")[1]
        de_name = file.split("/")[2].split("_")[2]
        try:
            all_sizes[f"{distro_name}_{distro_version}"][de_name] = float(data)
        except KeyError:
            all_sizes[f"{distro_name}_{distro_version}"] = {de_name: float(data)}

    # Sometimes the builder script fails due to a network error -> the size is 0 -> replace with old size
    # open old sizes file
    # with open("os_sizes.json", "r") as f:
    #     old_sizes = json.load(f)
    # for distro in all_sizes:
    #     for key in all_sizes[distro]:
    #         if all_sizes[distro][key] == 0:
    #             all_sizes[distro][key] = old_sizes[distro][key]

    # # Calculate average sizes
    # for distro in all_sizes:
    #     total_GB = 0
    #     total_amount = 0
    #     for key in all_sizes[distro]:
    #         total_GB += all_sizes[distro][key]
    #         total_amount += 1
    #     # calculate average size and cast to 1 decimal place
    #     all_sizes[distro]["average"] = round(total_GB / total_amount, 1)

    # Calculate raw DE sizes
    for distro in all_sizes:
        for key in all_sizes[distro]:
            if key != "cli":
                with contextlib.suppress(KeyError):  # the distro_average dicts obv don't have a cli key
                    all_sizes[distro][key] = round(all_sizes[distro][key] - all_sizes[distro]["cli"] / 2, 1)

    # Calculate average sizes for distros with multiple versions
    all_sizes["ubuntu_average"] = round(
        (all_sizes["ubuntu_22.04"]["cli"] + all_sizes["ubuntu_22.10"]["cli"]) / 2, 1)
    all_sizes["fedora_average"] = round((all_sizes["fedora_37"]["cli"] + all_sizes["fedora_38"]["cli"]) / 2, 1)

    with open("os_sizes.json", "w") as f:
        json.dump(all_sizes, f)
