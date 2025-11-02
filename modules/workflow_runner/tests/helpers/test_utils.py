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
    spec = importlib.util.spec_from_file_location("wf_helpers", str(helper_path))
    mod = importlib.util.module_from_spec(spec)
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
