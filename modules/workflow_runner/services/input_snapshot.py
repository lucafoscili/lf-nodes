"""Small, JSON-safe snapshots of workflow-runner submission inputs.

Snapshots are deliberately a convenience for history/remix UIs, not a copy of
the request or uploaded media.  Keep this policy close to the persistence
boundary so every storage adapter applies the same limits.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from typing import Any


# A normal workflow form is a few KB at most.  This budget leaves room for a
# useful prompt/control set while making accidental data-URL or metadata input
# harmless to both SQLite and the detail response.
INPUT_SNAPSHOT_MAX_BYTES = 64 * 1024
INPUT_SNAPSHOT_MAX_STRING_CHARS = 4096
INPUT_SNAPSHOT_MAX_ITEMS = 256
INPUT_SNAPSHOT_MAX_DEPTH = 16

_TRUNCATED = "[omitted: input value exceeded snapshot policy]"
_DEPTH_LIMIT = "[omitted: input nesting exceeded snapshot policy]"
_ITEM_LIMIT = "[omitted: input item limit exceeded snapshot policy]"
_BUDGET_LIMIT = "[omitted: input snapshot exceeded budget]"
_SENSITIVE = "[omitted: sensitive input]"


def _is_sensitive_key(value: str) -> bool:
    """Recognize credential-shaped form keys without hiding normal controls."""

    snake_case = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    normalized = re.sub(r"[^a-z0-9]+", "_", snake_case.lower()).strip("_")
    if not normalized:
        return False
    parts = normalized.split("_")
    if normalized in {"api_key", "apikey", "auth", "authorization", "bearer", "token"}:
        return True
    if any(part in {"password", "passwd", "pwd", "secret", "credential", "credentials"} for part in parts):
        return True
    if parts[-1] == "token":
        return True
    return len(parts) >= 2 and parts[-2:] in (["api", "key"], ["private", "key"], ["access", "key"])


def _is_data_url(value: str) -> bool:
    return value[:64].lower().startswith("data:") and ";base64," in value[:256].lower()


def _sanitize(value: Any, *, depth: int, key: str | None = None) -> Any:
    if key is not None and _is_sensitive_key(key):
        return _SENSITIVE
    if depth > INPUT_SNAPSHOT_MAX_DEPTH:
        return _DEPTH_LIMIT
    if value is None or isinstance(value, (bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, str):
        # A data URL is never useful for a remix form: file-backed upload
        # references are the canonical input representation.
        if _is_data_url(value):
            return _TRUNCATED
        if len(value) > INPUT_SNAPSHOT_MAX_STRING_CHARS:
            return value[: INPUT_SNAPSHOT_MAX_STRING_CHARS - 1] + "…"
        return value
    if isinstance(value, (bytes, bytearray, memoryview)):
        return _TRUNCATED
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for index, (raw_key, child) in enumerate(value.items()):
            if index >= INPUT_SNAPSHOT_MAX_ITEMS:
                result["_truncated_items"] = _ITEM_LIMIT
                break
            normalized_key = str(raw_key)[:INPUT_SNAPSHOT_MAX_STRING_CHARS]
            result[normalized_key] = _sanitize(
                child,
                depth=depth + 1,
                key=normalized_key,
            )
        return result
    if isinstance(value, (list, tuple)):
        result = [
            _sanitize(item, depth=depth + 1, key=key)
            for item in value[:INPUT_SNAPSHOT_MAX_ITEMS]
        ]
        if len(value) > INPUT_SNAPSHOT_MAX_ITEMS:
            result.append(_ITEM_LIMIT)
        return result
    # JSON requests should not contain these, but retaining a bounded textual
    # representation keeps adapter callers migration-safe and deterministic.
    return _sanitize(str(value), depth=depth, key=key)


def sanitize_input_snapshot(value: Any) -> dict[str, Any]:
    """Return a bounded JSON-safe mapping suitable for durable job history.

    The result is capped at ``INPUT_SNAPSHOT_MAX_BYTES`` after recursive
    normalization.  If even the normalized structure is too large, the
    snapshot is replaced by one explicit sentinel rather than storing a
    partial or potentially sensitive payload.
    """

    normalized = _sanitize(value if isinstance(value, Mapping) else {}, depth=0)
    if not isinstance(normalized, dict):
        normalized = {}
    try:
        encoded = json.dumps(
            normalized,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        return {"_truncated": _BUDGET_LIMIT}
    if len(encoded) > INPUT_SNAPSHOT_MAX_BYTES:
        return {"_truncated": _BUDGET_LIMIT}
    return normalized


__all__ = [
    "INPUT_SNAPSHOT_MAX_BYTES",
    "INPUT_SNAPSHOT_MAX_DEPTH",
    "INPUT_SNAPSHOT_MAX_ITEMS",
    "INPUT_SNAPSHOT_MAX_STRING_CHARS",
    "sanitize_input_snapshot",
]
