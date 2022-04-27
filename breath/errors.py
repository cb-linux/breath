"""
Breath Exceptions
"""

__all__ = (
    'BreathException',
    'PlatformNotSupported',
    'DistributionNotSupported',
    'UndeterminedSystem',
    'YayNotFound',
    'DontRunAsRoot',
    'DirectoryNotEmpty',
    'FileNotFound'
)

class BreathException(Exception):
    """
    Base exception class for Breath
    Used on exceptions raised from this library
    """

    pass


class PlatformNotSupported(BreathException):
    """
    Exception that is raised when the detected
    host system platform is not supported.
    """

    pass


class DistributionNotSupported(BreathException):
    """
    Exception that is raised when the detected
    host system distribution is not supported.
    """

    pass


class UndeterminedSystem(BreathException):
    """
    Exception that is raised when the host
    system name cannot be detected.
    """

    pass


class YayNotFound(BreathException):
    """
    Exception that is raised when an arch-based host
    system does not have the yay aur helper installed.
    """

    pass


class DontRunAsRoot(BreathException):
    """
    Exception that is raised when the Breath
    installer is run as root.
    """

    pass


class DirectoryNotEmpty(BreathException):
    """
    Exception that is raised when the Breath
    installer conflicts with existing system files.
    """

    pass


class FileNotFound(BreathException):
    """
    Exception that is raised when the Breath
    installer cannot find a needed file.
    """

    pass
