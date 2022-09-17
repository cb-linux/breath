# FILE SOURCE: https://github.com/apacelus/pathlib-functions
from pathlib import Path
import subprocess
import sys


#######################################################################################
#                               PATHLIB FUNCTIONS                                     #
#######################################################################################
# unlink all files in a directory and remove the directory
def rmdir(rm_dir: str, keep_dir: bool = True) -> None:
    def unlink_files(path_to_rm: Path) -> None:
        try:
            for file in path_to_rm.iterdir():
                if file.is_file():
                    file.unlink()
                else:
                    unlink_files(path_to_rm)
        except FileNotFoundError:
            # Directory doesn't exist
            return

    # convert string to Path object
    rm_dir_as_path = Path(rm_dir)
    unlink_files(rm_dir_as_path)
    # Remove emtpy directory
    if not keep_dir:
        try:
            rm_dir_as_path.rmdir()
        except FileNotFoundError:
            # Directory doesn't exist
            return


# remove a single file
def rmfile(file: str) -> None:
    file_as_path = Path(file)
    if file_as_path.exists():
        file_as_path.unlink()


# make directory
def mkdir(mk_dir: str, create_parents: bool = False) -> None:
    mk_dir_as_path = Path(mk_dir)
    if not mk_dir_as_path.exists():
        mk_dir_as_path.mkdir(parents=create_parents)


def path_exists(path: str) -> bool:
    path = Path(path)
    return path.exists()


def get_full_path(path: str) -> str:
    return Path(path).absolute().as_posix()


# recursively copy files from a dir into another dir
def cpdir(root_src: str, root_dst: str) -> None:  # dst_dir must be a full path, including the new dir name
    def copy_files(src: Path, dst: Path) -> None:
        # create dst dir if it doesn't exist
        mkdir(dst.absolute().as_posix(), create_parents=True)
        for src_file in src.iterdir():
            if src_file.is_file():
                dst_file = dst.joinpath(src_file.stem + src_file.suffix)
                dst_file.write_bytes(src_file.read_bytes())
            else:
                new_dst = dst.joinpath(src_file.stem)
                copy_files(src_file, new_dst)

    src_as_path = Path(root_src)
    dst_as_path = Path(root_dst)
    if src_as_path.exists():
        copy_files(src_as_path, dst_as_path)
    else:
        print("Source directory does not exist?")


def cpfile(src: str, dst: str) -> None:
    src_as_path = Path(src).absolute()
    dst_as_path = Path(dst).absolute()
    if src_as_path.exists():
        dst_as_path.write_bytes(src_as_path.read_bytes())
    else:
        print("Source file does not exist?")


#######################################################################################
#                               SUBPROCESS FUNCTIONS                                  #
#######################################################################################

# return the output of a command
def bash_return(command: str) -> str:
    return subprocess.check_output(command, shell=True, text=True).strip()


# print output of a command to console
def bash(command: str) -> None:
    subprocess.run(command, stderr=sys.stderr, stdout=sys.stdout, shell=True)
