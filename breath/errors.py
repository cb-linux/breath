"""
Exeption handler for Breath
"""

__all__ = (
    'BreathException',
    'SystemNotSupported',
    'DistributionNotSupported',
    'UndeterminedSystem'
    )

class BreathException(Exception):
    """
    Base exception class for Breath
    Used on exceptions raised from this library
    """

    pass


class SystemNotSupported(BreathException):
    """
    Exception that is raised when the detected
    host system is not supported.
    """

    pass


class DistributionNotSupported(BreathException):
    """
    Exception that is raised when the detected
    host distribution is not supported.
    """

    pass


class UndeterminedSystem(BreathException):
    """
    Exception that is raised when the host
    system name cannot be detected.
    """

    pass
