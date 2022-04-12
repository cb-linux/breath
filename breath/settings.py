"""
General configuration
"""

import sys

def set_verbosity_level(verbosity):
    """
    Hides traceback if --verbose flas is not set.
    """

    if verbosity == False:
        sys.tracebacklimit = 0

    else:
        pass
