import logging

# Centralized config handles .env loading for the workflow_runner package.
# Avoid duplicate local .env loaders in submodules; import config early so
# settings are computed before route registration.
try:
    from .config import get_settings  # noqa: F401
    _ = get_settings()
except Exception:
    logging.debug("Could not import workflow_runner.config early (continuing)")

# Import smaller modules which now contain the route handlers and assets.
from . import handlers  # registers routes when imported
