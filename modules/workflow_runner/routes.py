import os
import logging
from pathlib import Path

# Dev dotenv loader: load `.env` for local dev. The loader will run if either:
#  - DEV_ENV=1 is already set in the environment, OR
#  - a .env file exists next to this module (convenience for local dev).
try:
    env_path = Path(__file__).parent / ".env"
    should_load = os.environ.get("DEV_ENV") == "1" or env_path.exists()
    if should_load and env_path.exists():
        # lightweight loader to avoid adding a runtime dependency
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and not os.environ.get(k):
                os.environ[k] = v
except Exception:
    logging.exception('Failed to load local .env')

# Ensure the central config is imported early so submodules see consistent env-derived settings
try:
    from .config import get_settings  # noqa: F401
    _ = get_settings()
except Exception:
    logging.debug("Could not import workflow_runner.config early (continuing)")

# Import smaller modules which now contain the route handlers and assets.
from . import handlers  # registers routes when imported
