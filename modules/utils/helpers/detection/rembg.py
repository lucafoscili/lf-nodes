from __future__ import annotations

import os
import threading

from pathlib import Path
from rembg import new_session
from typing import Any

from ....utils.constants import ONNX_ROOT

_SESSION_CACHE: dict[str, Any] = {}
_SESSION_LOCK = threading.Lock()
_MODEL_DIR = Path(ONNX_ROOT) / "rembg"

def _ensure_model_dir() -> Path:
    """
    Ensures that the model directory exists and sets the 'U2NET_HOME' environment variable.

    Creates the directory specified by _MODEL_DIR if it does not already exist,
    including any necessary parent directories. Sets the 'U2NET_HOME' environment
    variable to the path of the model directory if it is not already set.

    Returns:
        Path: The path to the model directory.
    """
    _MODEL_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("U2NET_HOME", str(_MODEL_DIR))
    return _MODEL_DIR


def get_rembg_session(model_name: str = "u2net") -> Any:
    """
    Returns a cached rembg session for the specified model name.

    This function ensures that only one session per model is created and reused.
    If no model name is provided, it defaults to "u2net". The session is created
    if it does not already exist in the cache, otherwise the cached session is returned.

    Args:
        model_name (str, optional): The name of the rembg model to use. Defaults to "u2net".

    Returns:
        Any: A rembg session object for the specified model.
    """
    if not model_name:
        model_name = "u2net"

    with _SESSION_LOCK:
        session = _SESSION_CACHE.get(model_name)
        if session is not None:
            return session

        _ensure_model_dir()
        session = new_session(model_name)
        _SESSION_CACHE[model_name] = session
        return session