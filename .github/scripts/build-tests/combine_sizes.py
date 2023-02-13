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
        all_sizes[distro_name] = data

    with open("os_sizes.json", "w") as f:
        json.dump(all_sizes, f)
