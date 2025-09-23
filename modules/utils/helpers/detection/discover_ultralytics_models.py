from __future__ import annotations

from pathlib import Path
from typing import Dict

from ...constants import ONNX_ROOT

# region discover_ultralytics_models
def discover_ultralytics_models() -> Dict[str, Path]:
    """
    Discovers ONNX model files within the ONNX_ROOT directory and returns a dictionary mapping model labels to their file paths.

    Returns:
        Dict[str, Path]: A dictionary where keys are model labels (relative paths or file names) and values are the corresponding Path objects to ONNX model files.

    Notes:
        - If ONNX_ROOT does not exist or is inaccessible, returns an empty dictionary.
        - Model labels are generated as relative paths from ONNX_ROOT, using forward slashes.
        - Handles exceptions when checking for ONNX_ROOT existence and when computing relative paths.
    """
    discovered: Dict[str, Path] = {}
    try:
        root_exists = ONNX_ROOT.exists()
    except OSError:
        root_exists = False
    if not root_exists:
        return discovered
    for file in sorted(ONNX_ROOT.rglob("*.onnx")):
        try:
            relative = file.relative_to(ONNX_ROOT)
        except ValueError:
            label = file.name
        else:
            label = str(relative).replace("\\", "/")
        discovered[label] = file
    return discovered
# endregion