import subprocess
import platform
import distro
import sys

from .errors import *

def determine_system():
    system = platform.system()

    if system in ('Linux'):
        # Determine linux distribution
        dist = distro.id()

        # Raise error if distro not supported
        if dist not in ('arch', 'debian', 'fedora', 'ubuntu'):
            raise DistributionNotSupported(f"{dist} is not currently supported!")

    # [backlog] TODO: Add support for Windows and Darwin systems
    elif system in ('Windows', 'Darwin'):
        raise SystemNotSupported(f"{system} is not currently supported!")

    # Undetermined systems unsupported
    elif system is None:
        raise UndeterminedSystem("The host system platform could not be determined!")

    return system, dist








        



    
