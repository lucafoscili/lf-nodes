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
# Import controller submodules explicitly to ensure their route decorators run
# during package initialization. Using importlib avoids relying on
# `controllers.__init__` to re-export submodules and makes the import order
# explicit and robust during refactors.
import importlib
import logging

for mod in (
    "lf_nodes.modules.workflow_runner.controllers.api_routes",
    "lf_nodes.modules.workflow_runner.controllers.page_controller",
    "lf_nodes.modules.workflow_runner.controllers.assets_controller",
    "lf_nodes.modules.workflow_runner.controllers.proxy_controller",
):
    try:
        importlib.import_module(mod)
        logging.info("Imported workflow_runner controller: %s", mod)
    except Exception:
        logging.debug("Could not import %s during workflow_runner startup; continuing", mod)
