import json
import glob

if __name__ == "__main__":
    # open the sizes files in each result's directory
    files = glob.glob("./results-*/sizes*.json")
    all_sizes = {}
    for file in files:
        with open(file) as f:
            data = json.load(f)
        distro_name = file.split("/")[2][6:-5]
        # The latter scripts require an underscore at the end of the distro name
        # -> add it to distros that don't have subversions
        if not distro_name.__contains__("_"):
            distro_name = f"{distro_name}_"
        all_sizes[distro_name] = data

    # Sometimes the builder script fails due to a network error -> the size is 0 -> replace with old size
    # open old sizes file
    with open("os_sizes.json", "r") as f:
        old_sizes = json.load(f)
    for distro in all_sizes:
        for key in all_sizes[distro]:
            if all_sizes[distro][key] == 0:
                all_sizes[distro][key] = old_sizes[distro][key]

    # Calculate average sizes
    for distro in all_sizes:
        total_GB = 0
        total_amount = 0
        for key in all_sizes[distro]:
            total_GB += all_sizes[distro][key]
            total_amount += 1
        # calculate average size and cast to 1 decimal place
        all_sizes[distro]["average"] = round(total_GB / total_amount, 1)

    with open("os_sizes.json", "w") as f:
        json.dump(all_sizes, f)
