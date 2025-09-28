from __future__ import annotations

# region normalize_hex_color
def normalize_hex_color(color: str | None) -> str:
    """Normalize a hex color string to the form ``#RRGGBB``.

    Args:
        color: The input color string. Accepts values with or without a leading
            ``#`` and three- or six-character hex representations. ``None``
            falls back to black.

    Returns:
        str: The normalized hex color code in uppercase ``#RRGGBB`` format. If
        the input is invalid the fallback ``#000000`` is returned.
    """
    value = (color or "#000000").strip()
    if not value.startswith("#"):
        value = f"#{value}"
    if len(value) == 4:  # #RGB shorthand
        value = "#" + "".join(component * 2 for component in value[1:])
    if len(value) != 7:
        return "#000000"
    return value.upper()
# endregion
