"""
Breath user interactions
"""

def determine_configuration(defaults, user_input):
    """
    Determine if the user has set any flags.
    If the flags are all default and '--forcedefaults'
    is not set, guide user through a cli installer.
    Returns dict(new_options).
    """

    # Keep user_input the same if forcedefaults is set
    if user_input['forcedefaults'] == True:
        return user_input

    # Guide user through a cli installer if defaults match user_input
    if user_input == defaults:
        # TODO: Guide user through a cli installer.
        pass

    # If the user configured installation via argparse, skip cli config
    else:
        return user_input





