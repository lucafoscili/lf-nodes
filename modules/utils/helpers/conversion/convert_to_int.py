# region convert_to_int
def convert_to_int(text):
    """
    Convert a given text to an integer.

    Args:
        text (str): The text to be converted to an integer.

    Returns:
        int or None: The converted integer if successful, otherwise None if conversion fails.
    """
    try:
        return int(text)
    except ValueError:
        return None
# endregion