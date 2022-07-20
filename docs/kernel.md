## Building the Kernel

### Requirements
The following must be installed in order to successfully build the kernel:
* linux-generic (headers)
* bison (parser, replacement for yacc)
* flex (lexical scanner)
* libelf-dev (for Ubuntu; possibly libelf-devel or elfutils-libelf-devel for other distros)
* imagemagick (provides mogrify command)
* libssl-dev (supports openssl development)

### New build script
In the kernel folder, you should run the `build.sh` for a guided kernel build.

### Manually

Millions of lines of code have been poured into the Linux Kernel, along with thousands contributed by Google Engineers.

To honor their contributions and give to the open-source community, this project is free and open-source.

The installer of this project, which you are currently on, downloads 2 things in binary format:

* The Linux Kernel Executable (vmlinuz/bzImage)
* A Tar Archive of the kernel modules

Both of which require a powerful computer and at least an hour of compilation, which many users this project is made for don't have. The GPL permits distributing binaries, as long as you give the source code of them. The source of the kernel and modules is [here](https://chromium.googlesource.com/chromiumos/third_party/kernel). You can follow the bellow directions to compile your own kernel.

1. Clone the repository with git by running:
```bash
git clone --branch chromeos-4.19 --depth 1 https://chromium.googlesource.com/chromiumos/third_party/kernel.git
cd kernel
```

2. Download the kernel `.config` file, and update it, by running:
```bash
wget https://raw.githubusercontent.com/cb-linux/kernel/main/kernel.conf -O .config
make olddefconfig
```

3. Compile the kernel by running:
```bash
make -j$(nproc)
```

The `bzImage` should be located in `arch/x86/boot/bzImage`.

Running `make -j$(nproc) modules_install INSTALL_MOD_PATH=[DIRECTORY]`, and then compressing the `[DIRECTORY]` should give you the compressed modules.
