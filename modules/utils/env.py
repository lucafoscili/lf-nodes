import logging
import os

from pathlib import Path
from typing import List

_LOG = logging.getLogger(__name__)

# region .env Loader
def maybe_load_dotenv(path: Path) -> None:
    """
    Load a simple .env file into os.environ without external deps.

    This function will not override existing environment variables.
    """
    if not path.exists():
        return
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and os.environ.get(k) is None:
                os.environ[k] = v
    except Exception:
        _LOG.exception("failed to load .env at %s", path)
# endregion

# region Helpers
def bool_env(key: str, default: bool = False) -> bool:
    v = os.environ.get(key)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

def list_env(key: str) -> List[str]:
    v = os.environ.get(key, "")
    if not v:
        return []
    parts = [p.strip() for p in v.replace(";", ",").split(",") if p.strip()]
    return parts

def int_env(key: str, default: int) -> int:
    v = os.environ.get(key)
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default

def str_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)
# endregion