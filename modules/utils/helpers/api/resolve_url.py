from urllib.parse import urlparse, parse_qs

# region resolve_url
def resolve_url(api_url: str):
    """
    Parses the given API URL and extracts the 'filename', 'type', and 'subfolder' query parameters.
    Args:
        api_url (str): The API URL containing query parameters.
    Returns:
        tuple: A tuple containing the values of 'filename', 'type', and 'subfolder' (str or None).
    """
    parsed_url = urlparse(api_url)
    query_params = parse_qs(parsed_url.query)

    filename = query_params.get("filename", [None])[0]
    file_type = query_params.get("type", [None])[0]
    subfolder = query_params.get("subfolder", [None])[0]

    return filename, file_type, subfolder
# endregion