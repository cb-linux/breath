echo $env:FEATURES

# Prepare for Crostini
# We mount it in /mnt/breath because /mnt already contains the user's files
if ($env:FEATURES -like "*CROSTINI*") {
    sudo mkdir /mnt/breath
}

# Import functions
. utils/functions.sh # Functions
# source utils/bootstrap.sh # Bootstrap Function
# source utils/partition.sh # USB Partitioning
# source utils/extract.sh   # Extract Rootfs
# source utils/system.sh    # Host OS Abstraction