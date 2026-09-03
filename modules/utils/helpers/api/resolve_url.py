from urllib.parse import urlparse, parse_qs

from .read_secret import read_secret

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


def local_proxy_request_options(api_url: str, headers: dict) -> dict:
    """Authenticate an internal LF proxy call, never an arbitrary endpoint.

    Canonical relative proxy paths resolve against this Comfy server. Absolute
    URLs keep their existing behavior, even if they name the same machine.
    Never follow a redirect while carrying the server-side proxy credential.
    These options belong to the HTTP transport, not the saved request payload.
    """
    from ...constants import API_ROUTE_PREFIX

    options = {"headers": dict(headers)}
    proxy_paths = (f"{API_ROUTE_PREFIX}/proxy/", f"/api{API_ROUTE_PREFIX}/proxy/")
    if not api_url.startswith(proxy_paths):
        return options
    path = urlparse(api_url).path
    # HTTP clients/routers normalize dot segments and encoded separators. LF's
    # proxy routes need neither escapes nor traversal: don't send a credential
    # when normalization could move this request outside the intended route.
    if (
        "%" in path
        or "\\" in api_url
        or any(ord(char) < 32 or ord(char) == 127 for char in api_url)
        or any(part in (".", "..") for part in path.split("/"))
    ):
        return options

    secret = read_secret("LF_PROXY_SECRET") or read_secret("GEMINI_PROXY_SECRET")
    if secret:
        options["headers"]["X-LF-Proxy-Secret"] = secret
        options["allow_redirects"] = False
    return options
