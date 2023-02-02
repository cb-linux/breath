import json
import glob

if __name__ == "__main__":
    # open the sizes files in each result's directory
    files = glob.glob("./results-*/sizes*.json")
    all_sizes = {}
    for file in files:
        with open(file) as f:
            data = json.load(f)
        all_sizes[file[6:-5]] = data

    with open("os_sizes.json", "w") as f:
        json.dump(all_sizes, f)
