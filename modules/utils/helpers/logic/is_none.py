# region is_none
def is_none(input):
    """
    Check if the input is either None or a string representation of "None".

    This function evaluates the input to determine if it is a value that is either None
    or the string "None". It returns False for any other valid input.

    Parameters:
    input (any type): The input to be checked.

    Returns:
    bool: True if input is None or "None"; otherwise, False.
    """
    return bool(input == None or str(input) == "None")
# endregion