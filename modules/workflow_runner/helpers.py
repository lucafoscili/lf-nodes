"""Compatibility shim.

The helpers implementation has moved to `utils.helpers`. This file keeps a
thin import shim so existing imports that reference
`workflow_runner.helpers._emit_run_progress` continue to work during the
refactor.
"""

from .utils.helpers import _emit_run_progress  # type: ignore

__all__ = ["_emit_run_progress"]
