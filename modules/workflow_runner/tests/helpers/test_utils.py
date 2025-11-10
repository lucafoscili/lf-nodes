import importlib.util

from pathlib import Path
from typing import Any

def find_workflow_runner_base(start: Path | str = None) -> Path:
    p = Path(start or __file__).resolve()
    base = next((x for x in p.parents if x.name == "workflow_runner"), None)
    if base is None:
        raise RuntimeError("could not locate workflow_runner ancestor")
    return base

def load_helpers_module() -> Any:
    """Dynamically load the controllers._helpers module for tests."""
    base = find_workflow_runner_base(__file__)
    helper_path = base / "controllers" / "_helpers.py"
    # To allow relative imports inside the helpers module to resolve without
    # modifying global sys.path, create lightweight package entries in
    # sys.modules and preload the utils.serialize module under the
    # package-qualified name. This keeps tests isolated and avoids creating
    # a real package on disk or changing runtime behavior for the main app.
    import sys
    import types

    # Preload package structure entries (no file-system effects)
    pkg_prefix = "lf_nodes.modules.workflow_runner"
    pkg_parts = ["lf_nodes", "lf_nodes.modules", "lf_nodes.modules.workflow_runner", "lf_nodes.modules.workflow_runner.controllers", "lf_nodes.modules.workflow_runner.utils"]
    for p in pkg_parts:
        if p not in sys.modules:
            sys.modules[p] = types.ModuleType(p)

    # Load utils.serialize into sys.modules under the package-qualified name
    utils_path = base / "utils" / "serialize.py"
    try:
        utils_spec = importlib.util.spec_from_file_location(pkg_prefix + ".utils.serialize", str(utils_path))
        utils_mod = importlib.util.module_from_spec(utils_spec)
        utils_spec.loader.exec_module(utils_mod)
        sys.modules[pkg_prefix + ".utils.serialize"] = utils_mod
    except Exception:
        # If utils can't be loaded, proceed — helpers may provide fallbacks.
        pass

    # Now load the helpers module with a package-qualified name so relative
    # imports inside it will resolve against the synthetic package entries.
    spec = importlib.util.spec_from_file_location(pkg_prefix + ".controllers._helpers", str(helper_path))
    mod = importlib.util.module_from_spec(spec)
    # Ensure module is registered under its package-qualified name
    sys.modules[spec.name] = mod
    # Set __package__ so relative imports in the module resolve
    mod.__package__ = pkg_prefix + ".controllers"
    spec.loader.exec_module(mod)
    return mod

class MockRequest:
    """Lightweight mock request used by multiple workflow_runner tests.

    - For JSON parsing tests it provides an async .json() method that either
      returns a pre-set payload or raises a pre-set exception.
    - For owner extraction tests it exposes a `_cache` dict and optional
      attributes and a dict-like `.get()`.
    """
    def __init__(self, payload=None, exc: Exception | None = None, cache: dict | None = None, attr: dict | None = None):
        # JSON payload style
        self._payload = payload
        self._exc = exc

        # owner extraction style
        self._cache = cache
        if attr:
            for k, v in attr.items():
                try:
                    setattr(self, k, v)
                except Exception:
                    pass

    async def json(self):
        if self._exc:
            raise self._exc
        return self._payload

    def get(self, key, default=None):
        if isinstance(self._cache, dict):
            return self._cache.get(key, default)
        return default