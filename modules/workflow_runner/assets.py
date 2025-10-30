"""Compatibility shim for assets.

Static asset logic has been moved to `controllers.assets_controller`. This
module re-exports the helpers so existing imports continue to work while the
refactor consolidates code.
"""

from .controllers.assets_controller import _serve_first_existing, _serve_static  # type: ignore

__all__ = ["_serve_first_existing", "_serve_static"]
