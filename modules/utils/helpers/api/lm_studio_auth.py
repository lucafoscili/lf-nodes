"""Server-side authentication for explicit LM Studio native API requests."""

from .read_secret import read_secret


def with_lm_studio_auth(options: dict) -> tuple[dict, str | None]:
    """Copy transport options and attach native API auth without saving secrets.

    Call only for LM Studio native routes, never generic compatible endpoints.
    Proxy headers and redirect policy are preserved; authenticated requests must
    not follow redirects that could move the token to a different endpoint.
    """
    authenticated = {**options, "headers": dict(options.get("headers", {}))}
    token = read_secret("LM_API_TOKEN")
    if token:
        authenticated["headers"]["Authorization"] = f"Bearer {token}"
        authenticated["allow_redirects"] = False
    return authenticated, token
