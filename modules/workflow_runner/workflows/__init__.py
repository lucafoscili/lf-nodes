from importlib import import_module
from types import ModuleType
from typing import Iterable, Iterator, Sequence

_WORKFLOW_MODULES: Sequence[str] = (
    "image_to_svg",
    "load_metadata",
    "simple_chat",
    "sort_json_keys",
    "svg_generation_gemini",
)

# region Workflow Imports
def _import_workflow_module(module_name: str) -> ModuleType:
    return import_module(f"{__name__}.{module_name}")

def iter_workflow_modules() -> Iterator[ModuleType]:
    for module_name in _WORKFLOW_MODULES:
        yield _import_workflow_module(module_name)

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