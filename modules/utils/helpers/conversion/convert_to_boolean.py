# region convert_to_boolean
def convert_to_boolean(text):
    """
    Convert a string to a boolean.

    Args:
        text (str): The input string to convert, typically representing a boolean value.

    Returns:
        bool or None: Returns True if the input string is 'true' or 'yes' (case-insensitive),
                      False if it is 'false', 'no', or an empty string.
                      Returns None if the input does not match any of those options.
    """
    if isinstance(text, bool):
        return text
    if text is None:
        return False

    text_lower = str(text).strip().lower()
    if text_lower in ['true', 'yes']:
        return True
    elif text_lower in ['false', 'no', '']:
        return False
    
    return None
# endregion