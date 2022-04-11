"""
Exception handler for Breath
"""

__all__ = (
    'BreathException',
    'SystemNotSupported'
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
    host system is not supported
    """

    pass
