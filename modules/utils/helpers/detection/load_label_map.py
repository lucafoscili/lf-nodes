from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import json

# region load_label_map
def load_label_map(model_path: Path) -> Optional[List[str]]:
    """
    Loads a label map from a file associated with the given model path.

    The function searches for label map files with various common suffixes
    (e.g., .json, .yaml, .yml, .labels, .names, .txt) in the same directory
    as the provided model path. It attempts to parse the file contents and
    extract a list of label names.

    Supported formats:
    - JSON: Either a list of labels or a dictionary mapping indices to labels.
    - YAML/TXT/LABELS/NAMES: Each line represents a label, optionally in "index: label" format.
    - Lines starting with '#' are ignored as comments.

    Args:
        model_path (Path): The path to the model file.

    Returns:
        Optional[List[str]]: A list of label names if a valid label map is found, otherwise None.
    """
    if not model_path:
        return None

    path = Path(model_path)
    suffixes = (".json", ".yaml", ".yml", ".labels", ".names", ".txt")
    candidates = []
    for suffix in suffixes:
        candidates.append(path.with_suffix(suffix))
        candidates.append(path.parent / f"{path.stem}{suffix}")
        if suffix in (".labels", ".txt"):
            candidates.append(path.parent / f"{path.stem}.labels.txt")

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            if not candidate.is_file():
                continue
        except OSError:
            continue
        try:
            content = candidate.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            continue
        if not content:
            continue

        suffix = candidate.suffix.lower()
        if suffix == ".json":
            try:
                parsed = json.loads(content)
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
                        label = str(value).strip()
                        if label:
                            items.append((idx, label))
                    if items:
                        items.sort(key=lambda item: item[0])
                        return [label for _, label in items]
                if isinstance(parsed, list):
                    labels = [str(item).strip() for item in parsed if str(item).strip()]
                    if labels:
                        return labels
            continue

        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]
        if not lines:
            continue

        labels: List[str] = []
        for line in lines:
            if ":" in line:
                possible_idx, possible_name = line.split(":", 1)
                if possible_idx.strip().isdigit():
                    name = possible_name.strip()
                    if name:
                        labels.append(name)
                        continue
            labels.append(line)
        if labels:
            return labels

    return None
# endregion