from .not_none import not_none

# region normalize_input_list
def normalize_input_list(input):
    """
    Standardizes the input into a list format if not already a list, handling edge cases 
    where the input might be None or an invalid type. If the input is None, empty, or 
    equivalent to "None", it returns None. Otherwise, it wraps non-list inputs in a list.

    Parameters:
    input (any type): The input value to be normalized into a list.

    Returns:
    list or None: A list if the input is valid, or None if input is empty or invalid.
    """
    if not_none(input):
        if isinstance(input, list) and len(input) > 0:
            return input
        elif isinstance(input, (str, int, float, bool, dict)):
            return [input]
        
    return None
# endregion