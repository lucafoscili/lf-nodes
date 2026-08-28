from __future__ import annotations

from typing import Any, Mapping


OWNER_CLIENT_ID_KEY = "owner_client_id"
CALLER_CLIENT_ID_FIELD = "caller_client_id"


def normalize_client_id(value: object) -> str | None:
    """Normalize one Comfy WebSocket client identifier."""
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None


def get_owner_client_id(container: Mapping[str, Any]) -> str | None:
    """Read a persisted owner, rejecting malformed non-empty representations."""
    if OWNER_CLIENT_ID_KEY not in container or container[OWNER_CLIENT_ID_KEY] is None:
        return None

    owner = normalize_client_id(container[OWNER_CLIENT_ID_KEY])
    if owner is None:
        raise ValueError("Editing context has an invalid owner client ID.")
    return owner


def caller_owns_context(
    container: Mapping[str, Any],
    caller_client_id: object,
) -> bool:
    """Authorize an owner-bound context or an exact ownerless headless context."""
    try:
        owner = get_owner_client_id(container)
    except ValueError:
        return False

    if owner is None:
        # The caller still had to present the exact unguessable context path to
        # retrieve ``container``. This is the intentional headless seam.
        return True
    return normalize_client_id(caller_client_id) == owner


__all__ = [
    "CALLER_CLIENT_ID_FIELD",
    "OWNER_CLIENT_ID_KEY",
    "caller_owns_context",
    "get_owner_client_id",
    "normalize_client_id",
]
