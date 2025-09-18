import importlib
import pkgutil

from typing import Callable, Dict, Any, Optional, List

Matcher = Callable[[Dict[str, Any], Dict[str, Any]], Optional[Dict[str, Any]]]

_DISCOVERED: List[Matcher] = []

def discover() -> List[Matcher]:
    global _DISCOVERED
    if _DISCOVERED:
        return _DISCOVERED
    pkg = __name__
    for info in pkgutil.iter_modules(__path__):  # type: ignore[name-defined]
        if info.name.startswith("_"):
            continue
        mod = importlib.import_module(f"{pkg}.{info.name}")
        if hasattr(mod, "register"):
            try:
                matchers = mod.register()
                if isinstance(matchers, list):
                    _DISCOVERED.extend(matchers)
            except Exception:
                continue
    return _DISCOVERED