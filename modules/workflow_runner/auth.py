"""Compatibility shim for auth.

Auth logic has moved into `services.auth_service`. This module keeps a
thin re-export shim so existing imports continue to work while the code is
being refactored.

Deprecation: importers should migrate to `workflow_runner.services.auth_service`.
"""

import warnings

warnings.warn(
    "workflow_runner.auth is deprecated and will be moved to "
    "workflow_runner.services.auth_service; import from the services package "
    "instead.",
    DeprecationWarning,
    stacklevel=2,
)

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

