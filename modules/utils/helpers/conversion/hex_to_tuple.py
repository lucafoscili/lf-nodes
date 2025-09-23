# region hex_to_tuple
def hex_to_tuple(color: str):
    """
    Converts a HEX color to a tuple.
    """
    return tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
# endregion