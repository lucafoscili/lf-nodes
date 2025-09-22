from __future__ import annotations

from typing import List, Optional

# region parse_class_filter
def parse_class_filter(raw_value: str) -> Optional[List[str]]:
    """
    Parses a raw string containing class names separated by commas or semicolons into a list of class names.

    Args:
        raw_value (str): The raw input string containing class names, separated by commas or semicolons.

    Returns:
        Optional[List[str]]: A list of stripped class names if any are found; otherwise, None.
    """
    tokens = [segment.strip() for segment in str(raw_value).replace(";", ",").split(",") if segment.strip()]
    return tokens or None
# endregion