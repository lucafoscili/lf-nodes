import fnmatch

# region filter_list
def filter_list(filter, list):
    """
    Filter a list of strings by applying a filter pattern.

    Args:
        filter (str): The filter pattern, supporting wildcards.
        list (List[str]): The list of strings to be filtered.

    Returns:
        List[str]: A filtered list of strings matching the pattern.
    """
    normalized_filter = filter.replace('\\', '/')
    return [model for model in list if fnmatch.fnmatch(model.replace('\\', '/'), normalized_filter)]
# endregion