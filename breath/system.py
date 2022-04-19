import subprocess
import platform
import distro
import sys

from .errors import *

# Define platform and system to be used throughout system.py
platform = platform.system()
distro = distro.id()

# Raise error if distro not supported
if distro not in ('arch', 'debian', 'fedora', 'ubuntu'):
    raise DistributionNotSupported(f"{distro} is not currently supported!")

# Windows and Darwin unsupported
elif platform in ('Windows', 'Darwin'):
    raise PlatformNotSupported(f"{platform} is not currently supported!")
