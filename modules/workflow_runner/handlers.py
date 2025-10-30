"""Compatibility shim for the legacy `handlers` module.

Routes and page-serving logic have been moved into `controllers/`.
This shim preserves the import path and registers the new controller
modules on import for backward compatibility while emitting a
DeprecationWarning to guide consumers to the new locations.
"""

import warnings

warnings.warn(
    "workflow_runner.handlers is deprecated and will be removed; import "
    "workflow_runner.controllers.* modules instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import controller modules which register their routes when imported.
import importlib

# Use absolute import via importlib to avoid relying on the package
# `controllers.__init__` to expose submodules as attributes. This is robust
# during the refactor and avoids the "cannot import name X from controllers"
# error seen when __init__.py doesn't re-export submodules.
try:
    importlib.import_module("lf_nodes.modules.workflow_runner.controllers.api_routes")
except Exception:
    # Best-effort import; failing here should not crash the shim import-time
    # because we want the application to continue starting where possible.
    pass

try:
    importlib.import_module("lf_nodes.modules.workflow_runner.controllers.page_controller")
except Exception:
    pass

try:
    importlib.import_module("lf_nodes.modules.workflow_runner.controllers.assets_controller")
except Exception:
    pass

try:
    importlib.import_module("lf_nodes.modules.workflow_runner.controllers.proxy_controller")
except Exception:
    pass

__all__ = []
