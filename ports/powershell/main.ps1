echo $env:FEATURES

# Prepare for Crostini
# We mount it in /mnt/breath because /mnt already contains the user's files
if ($env:FEATURES -like "*CROSTINI*") {
    sudo mkdir /mnt/breath
}

# Import functions
. utils/functions.ps1 # Functions
. utils/bootstrap.ps1 # Bootstrap Function
. utils/partition.sh # USB Partitioning
. utils/extract.sh   # Extract Rootfs
. utils/system.sh    # Host OS Abstraction