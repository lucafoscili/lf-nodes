# region normalize_list_item
def normalize_list_item(l: list, i: int):
    """
    Normalize the item at the specified index in a list.

    This function checks if the input is a list and if the specified
    index is within the bounds of the list. It returns the item at
    the specified index if valid, otherwise, returns the first item.

    Args:
        l (list): The list from which the item is retrieved.
        i (int): The index of the item to retrieve.

    Returns:
        any: The item at the specified index, or the first item if
             the index is invalid or not a list.
    """
    return l[i] if isinstance(l, list) and i < len(l) else l[0]
# endregion