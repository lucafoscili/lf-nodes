"""Workflow runner package exports.

Expose a small, stable public surface. Import the registry implementation
directly from the services package to avoid depending on the removed
root-level shim (`registry.py`).
"""

# Lazy-forward registry symbols to avoid importing heavy dependencies when
# the package is imported for side-effect-free operations (for example, when
# running static workflow preflight and node-count tooling). This defers both
# runtime configuration and the canonical registry until a caller uses them.
def __getattr__(name: str):
    if name == "CONFIG":
        from .config import CONFIG

        return CONFIG
    if name in ("REGISTRY", "get_workflow", "list_workflows"):
        from .services import registry as _registry

        return getattr(_registry, name)
    raise AttributeError(name)


def __dir__():
    return ["CONFIG", "REGISTRY", "get_workflow", "list_workflows"]

__all__ = ["CONFIG", "REGISTRY", "get_workflow", "list_workflows"]
