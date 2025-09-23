from __future__ import annotations

from typing import List, Optional

import json
import re

# region parse_class_labels
def parse_class_labels(raw_value: str) -> Optional[List[str]]:
    """
    Parses a raw string input representing class labels from a UI, supporting multiple formats.

    Args:
        raw_value (str): The raw input string containing class labels. Can be a JSON list, JSON dict, or a delimited string.

    Returns:
        Optional[List[str]]: A list of parsed class label strings, or None if input is empty or invalid.

    Supported formats:
        - JSON list: e.g., '["cat", "dog"]'
        - JSON dict: e.g., '{"0": "cat", "1": "dog"}' (sorted by key)
        - Delimited string: e.g., 'cat, dog;bird'

    Notes:
        - Ignores empty or whitespace-only labels.
        - Returns None if no valid labels are found.
    """
    if raw_value is None:
        return None
    
    text = str(raw_value).strip()
    if not text:
        return None
    
    if text[0] in "[{":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        else:
            if isinstance(parsed, dict):
                items = []
                for key, value in parsed.items():
                    try:
                        idx = int(key)
                    except (TypeError, ValueError):
                        continue
                    name = str(value).strip()
                    if name:
                        items.append((idx, name))
                if items:
                    items.sort(key=lambda item: item[0])
                    return [name for _, name in items]
            if isinstance(parsed, list):
                labels = [str(item).strip() for item in parsed if str(item).strip()]
                if labels:
                    return labels
    segments = re.split(r"[,;\n]+", text)
    labels = [segment.strip() for segment in segments if segment.strip()]

    return labels or None
# endregion