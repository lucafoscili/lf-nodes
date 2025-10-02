import os
import re
from typing import Optional

SAFE_FILENAME_FALLBACK = "image"
SAFE_EXT_FALLBACK = "png"

# region sanitize_filename
def sanitize_filename(
    value: str,
    *,
    default_stem: str = SAFE_FILENAME_FALLBACK,
    default_ext: str = SAFE_EXT_FALLBACK,
) -> Optional[str]:
    """
    Normalize a user-supplied filename into a safe "stem.ext" pair.

    The filename is restricted to its basename, stripped of path separators,
    and limited to ASCII letters, numbers, dots, underscores, and hyphens.
    If the stem or extension is missing, fallback values are applied.

    Args:
        value: The raw filename string from the user.
        default_stem: Fallback stem name when the sanitized value is empty.
        default_ext: Fallback file extension (without dot) when missing.

    Returns:
        A sanitized filename in the form ``stem.ext`` (lowercased extension),
        or ``None`` if the value cannot be safely normalized.
    """
    candidate = (value or "").strip()
    if not candidate:
        return None

    candidate = candidate.replace("\\", "/")
    candidate = os.path.basename(candidate)
    if not candidate or candidate in {".", ".."}:
        return None

    stem, ext = os.path.splitext(candidate)
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._")
    safe_ext = re.sub(r"[^A-Za-z0-9]", "", ext.lstrip("."))

    if not safe_stem:
        safe_stem = default_stem
    if not safe_ext:
        safe_ext = default_ext

    return f"{safe_stem}.{safe_ext.lower()}"
# endregion
