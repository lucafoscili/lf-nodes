from importlib import import_module
from types import ModuleType
from typing import Iterable, Iterator, Sequence
import pkgutil

_WORKFLOW_MODULES: Sequence[str] = (
    "caption_image_vision",
    "image_to_svg",
    "load_metadata",
    "remove_bg",
    "simple_chat",
    "sort_json_keys",
    "svg_generation_gemini",
    "t2i_15_lcm",
)

# region Workflow Imports
def _import_workflow_module(module_name: str) -> ModuleType:
    return import_module(f"{__name__}.{module_name}")

def iter_workflow_modules() -> Iterator[ModuleType]:
    for module_name in _WORKFLOW_MODULES:
        yield _import_workflow_module(module_name)

    try:
        custom_pkg = import_module(f"{__name__}.custom")
    except ModuleNotFoundError:
        custom_pkg = None

    if custom_pkg is not None and hasattr(custom_pkg, "__path__"):
        for _, name, _ in pkgutil.iter_modules(custom_pkg.__path__):
            module_name = f"custom.{name}"
            try:
                yield _import_workflow_module(module_name)
            except Exception:
                continue

def iter_workflow_definitions() -> Iterable[object]:
    """
    Yield each workflow definition exported by the configured workflow modules.

    Modules can expose either:
      * WORKFLOWS: an iterable of WorkflowNode instances, or
      * WORKFLOW: a single WorkflowNode instance.
    """
    for module in iter_workflow_modules():
        definitions = getattr(module, "WORKFLOWS", None)
        if definitions is None:
            single_definition = getattr(module, "WORKFLOW", None)
            definitions = () if single_definition is None else (single_definition,)

        if isinstance(definitions, (list, tuple, set)):
            for definition in definitions:
                if definition is not None:
                    yield definition
        elif definitions is not None:
            yield definitions
# endregion