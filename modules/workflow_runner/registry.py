"""Compatibility shim that re-exports the registry implementation from
``services.registry``. The implementation lives in ``services/registry.py``;
this shim preserves the original import path while the refactor completes.
"""

import warnings
from typing import Any

# Emit a deprecation warning immediately so imports see the message, but avoid
# importing the implementation at module-import time to prevent circular imports
# while the refactor is in progress. The actual implementation is lazily
# imported on first attribute access via __getattr__ (PEP 562).
warnings.warn(
    "workflow_runner.registry is deprecated and will be moved to "
    "workflow_runner.services.registry; import from the services package "
    "instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Cache for the real implementation module once loaded
_impl: Any | None = None


def _load_impl() -> Any:
    """Lazy-import and cache the implementation module.

    This defers importing ``.services.registry`` until one of the exported
    names is actually accessed which prevents import-time execution in the
    implementation that previously caused circular-import errors.
    """
    global _impl
    if _impl is None:
        # Local import to avoid import-time cycles
        from .services import registry as _registry_impl

        _impl = _registry_impl
    return _impl


def __getattr__(name: str) -> Any:  # pragma: no cover - trivial forwarding
    impl = _load_impl()
    try:
        return getattr(impl, name)
    except AttributeError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc


def __dir__() -> list[str]:
    # Provide a helpful dir() listing that includes the implementation's public names
    impl = _load_impl()
    impl_names = [n for n in dir(impl) if not n.startswith("_")]
    return sorted(set(list(globals().keys()) + impl_names))


# Public surface maintained for compatibility. Accessing these names will lazily
# load and forward to the implementation in ``services.registry``.
__all__ = [
    "InputValidationError",
    "WorkflowCell",
    "WorkflowNode",
    "WorkflowRegistry",
    "REGISTRY",
    "list_workflows",
    "get_workflow",
]
