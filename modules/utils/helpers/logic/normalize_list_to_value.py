from .not_none import not_none

# region normalize_list_to_value
def normalize_list_to_value(input):
    """
    Returns the first element of a list if it contains valid, non-null data, or the input itself otherwise.
    
    This function checks whether the input is a list and has valid contents as defined by `not_none(input)`.
    If these conditions are met, the first element of the list is returned. If the input is not a list 
    or does not meet these validity criteria, the function returns the input as-is.

    Parameters:
    input (any): The input, expected to be a list or other value.

    Returns:
    any: The first element of the list if input is a valid list; otherwise, the input itself.
    """
    if isinstance(input, list) and not_none(input):
        return input[0]
    return input
# endregion