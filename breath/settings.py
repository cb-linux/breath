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


def input_options(options):
    """
    Installation inputs if --forcedefaults 
    was not used and no defaults were changed.
    """

    # TODO: Implement input_options



