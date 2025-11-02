"""Compatibility shim for tests that import
`modules.workflow_runner.controllers.routes`.

This module simply imports the real API route registrations in
`api_routes.py` so tests and callers that import the `routes` submodule
will succeed. Keeping the shim minimal avoids duplicating route
registration logic and keeps import-time work small.
"""
from . import api_routes  # noqa: F401  (import for side-effects: route registration)

__all__ = []
