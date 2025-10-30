"""Proxy shim - re-exports the proxy controller to preserve old import behavior.

Importing this module registers the proxy routes (via the controller module).
"""

from .controllers import proxy_controller  # noqa: F401 - registers routes on import

__all__ = ["proxy_controller"]
