"""Proxy shim - re-exports the proxy controller to preserve old import behavior.

Importing this module registers the proxy routes (via the controller module).

Deprecation: importers should migrate to `workflow_runner.controllers.proxy_controller`. Note:
this shim currently registers routes on import via the controller module.
"""

import warnings

warnings.warn(
	"workflow_runner.proxy is deprecated and will be removed; import "
	"workflow_runner.controllers.proxy_controller instead.",
	DeprecationWarning,
	stacklevel=2,
)

from .controllers import proxy_controller  # noqa: F401 - registers routes on import

__all__ = ["proxy_controller"]
