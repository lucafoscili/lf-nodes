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

# region resolve_api_url
def resolve_api_url(api_url: str) -> str:
    """
    Resolve an API URL that may be a path-only proxy (for example '/api/lf-nodes/proxy/kobold')
    into an absolute URL using the running PromptServer address/port and CLI TLS args.

    If api_url already contains a scheme (e.g. 'http://' or 'https://') it is returned
    unchanged.

    Returns:
        str: an absolute URL safe to pass to requests/aiohttp clients.
    """
    parsed = urlparse(api_url)

    if parsed and parsed.scheme:
        return api_url

    try:
        from comfy.cli_args import args as comfy_args
    except Exception:
        comfy_args = None

    try:
        from server import PromptServer
    except Exception:
        PromptServer = None

    scheme = "https" if (getattr(comfy_args, 'tls_keyfile', None) and getattr(comfy_args, 'tls_certfile', None)) else "http"

    host = '127.0.0.1'
    port = 8188
    if PromptServer and getattr(PromptServer, 'instance', None):
        host = getattr(PromptServer.instance, 'address', host)
        port = getattr(PromptServer.instance, 'port', port)

    path = api_url if api_url.startswith('/') else f'/{api_url}'
    return f"{scheme}://{host}:{port}{path}"
# endregion