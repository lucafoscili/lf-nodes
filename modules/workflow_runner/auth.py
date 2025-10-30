"""Compatibility shim for auth.

Auth logic has moved into `services.auth_service`. This module keeps a
thin re-export shim so existing imports continue to work while the code is
being refactored.
"""

from .services.auth_service import *  # type: ignore

__all__ = [
    "_ENABLE_GOOGLE_OAUTH",
    "_require_auth",
    "_WF_DEBUG",
    "create_server_session",
    "_extract_token_from_request",
    "_verify_session",
    "_verify_token_and_email",
    "_GOOGLE_CLIENT_IDS",
    "_SESSION_TTL",
]

from .services.auth_service import *  # re-export all symbols from service implementation

__all__ = [
    "_ENABLE_GOOGLE_OAUTH",
    "_require_auth",
    "_WF_DEBUG",
    "create_server_session",
    "_extract_token_from_request",
    "_verify_session",
    "_verify_token_and_email",
    "_GOOGLE_CLIENT_IDS",
    "_SESSION_TTL",
]

