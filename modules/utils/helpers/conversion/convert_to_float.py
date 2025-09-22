# region convert_to_float
def convert_to_float(text):
    """
    Convert a given text to a float.

    Args:
        text (str): The text to be converted to a float.

    Returns:
        float or None: The converted float if successful, otherwise None if conversion fails.
    """
    try:
        return float(text)
    except ValueError:
        return None
# endregion