"""Compatibility shim.

The helpers implementation has moved to `utils.helpers`. This file keeps a
thin import shim so existing imports that reference
`workflow_runner.helpers._emit_run_progress` continue to work during the
refactor.

Deprecation: importers should migrate to `workflow_runner.utils.helpers`.
"""

import warnings

warnings.warn(
	"workflow_runner.helpers is deprecated and will be moved to "
	"workflow_runner.utils.helpers; import from the utils package instead.",
	DeprecationWarning,
	stacklevel=2,
)

from .utils.helpers import _emit_run_progress  # type: ignore

__all__ = ["_emit_run_progress"]
