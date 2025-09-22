# region not_none
def not_none(input):
    """
    Check if the input is neither None nor a string representation of "None".

    This function evaluates the input to determine if it is a value that is neither None
    nor the string "None". It returns True for any other valid input.

    Parameters:
    input (any type): The input to be checked.

    Returns:
    bool: True if input is not None or "None"; otherwise, False.
    """
    return bool(input != None and str(input) != "None")
# endregion