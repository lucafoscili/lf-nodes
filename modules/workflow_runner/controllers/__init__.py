import importlib
import warnings

from typing import Any

__all__ = [
    "start_workflow_controller",
    "get_workflow_status_controller",
    "list_workflows_controller",
    "get_workflow_controller",
    "verify_controller",
    "debug_login_controller",
]

warnings.warn(
    "Importing names from workflow_runner.controllers is deprecated and will be removed; "
    "import workflow_runner.controllers.api_controllers or import submodules directly.",
    DeprecationWarning,
    stacklevel=2,
)

def _load_impl() -> Any:
    """Lazy-load the api_controllers implementation module."""
    return importlib.import_module("modules.workflow_runner.controllers.api_controllers")

def __getattr__(name: str) -> Any:  # pragma: no cover - trivial forwarding
    if name == "routes":
        return importlib.import_module("modules.workflow_runner.controllers.routes")

    if name in __all__:
        impl = _load_impl()
        try:
            return getattr(impl, name)
        except AttributeError as exc:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__() -> list[str]:
    impl = _load_impl()
    impl_names = [n for n in dir(impl) if not n.startswith("_")]
    return sorted(set(list(globals().keys()) + impl_names))