"""Compatibility shim for assets.

Static asset logic has been moved to `controllers.assets_controller`. This
module re-exports the helpers so existing imports continue to work while the
refactor consolidates code.

Deprecation: importers should migrate to `workflow_runner.controllers.assets_controller`.
"""

import warnings

warnings.warn(
	"workflow_runner.assets is deprecated and will be moved to "
	"workflow_runner.controllers.assets_controller; import from the controllers "
	"package instead.",
	DeprecationWarning,
	stacklevel=2,
)

from .controllers.assets_controller import _serve_first_existing, _serve_static  # type: ignore

__all__ = ["_serve_first_existing", "_serve_static"]
