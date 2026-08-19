from importlib import import_module
import logging
import os
from pathlib import Path
from types import ModuleType
from typing import Iterable, Iterator, Sequence
import pkgutil

_LOG = logging.getLogger(__name__)

_WORKFLOW_MODULES: Sequence[str] = (
    "caption_image_vision",
    "image_to_svg",
    "load_metadata",
    "remove_bg",
    "simple_chat",
    "sort_json_keys",
    "svg_generation_gemini",
    "t2i_15_lcm",
    "youtube_reference_intake",
)

# region Workflow Imports
def _import_workflow_module(module_name: str) -> ModuleType:
    return import_module(f"{__name__}.{module_name}")


def _resolve_extra_workflow_roots(
    raw_roots: Iterable[str | Path],
) -> tuple[Path, ...]:
    roots: list[Path] = []
    seen: set[Path] = set()
    for raw_root in raw_roots:
        candidate = Path(os.path.expandvars(str(raw_root))).expanduser()
        if not candidate.is_absolute():
            _LOG.warning("Ignoring relative Workflow Runner root: %s", candidate)
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError):
            _LOG.warning("Ignoring unavailable Workflow Runner root: %s", candidate)
            continue
        if not resolved.is_dir():
            _LOG.warning("Ignoring non-directory Workflow Runner root: %s", resolved)
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        roots.append(resolved)
    return tuple(roots)


def _extra_workflow_roots_from_settings() -> tuple[str, ...]:
    from ..config import get_settings

    configured = getattr(
        get_settings(),
        "WORKFLOW_RUNNER_EXTRA_WORKFLOW_ROOTS",
        (),
    )
    return tuple(configured or ())


def _configure_custom_package_paths(
    raw_roots: Iterable[str | Path],
) -> ModuleType | None:
    try:
        custom_pkg = import_module(f"{__name__}.custom")
    except ModuleNotFoundError:
        return None

    if getattr(custom_pkg, "__path__", None) is None:
        return None

    bundled_root = Path(__file__).with_name("custom").resolve()
    package_paths = [os.fspath(bundled_root)]
    for root in _resolve_extra_workflow_roots(raw_roots):
        root_text = os.fspath(root)
        if root_text not in package_paths:
            package_paths.append(root_text)
            _LOG.info("Registered external Workflow Runner root: %s", root)
    custom_pkg.__path__ = package_paths
    return custom_pkg


def _discover_custom_module_names(custom_pkg: ModuleType) -> tuple[str, ...]:
    discovered: dict[str, str] = {}
    for package_path in custom_pkg.__path__:
        for _, name, _ in pkgutil.iter_modules([package_path]):
            previous_path = discovered.get(name)
            if previous_path is not None:
                _LOG.warning(
                    "Ignoring duplicate Workflow Runner module %r from %s; "
                    "the module from %s takes precedence",
                    name,
                    package_path,
                    previous_path,
                )
                continue
            discovered[name] = package_path
    return tuple(sorted(discovered))


def iter_workflow_modules(
    extra_workflow_roots: Iterable[str | Path] | None = None,
) -> Iterator[ModuleType]:
    for module_name in _WORKFLOW_MODULES:
        yield _import_workflow_module(module_name)

    configured_roots = (
        _extra_workflow_roots_from_settings()
        if extra_workflow_roots is None
        else extra_workflow_roots
    )
    custom_pkg = _configure_custom_package_paths(configured_roots)

    if custom_pkg is not None and hasattr(custom_pkg, "__path__"):
        for name in _discover_custom_module_names(custom_pkg):
            module_name = f"custom.{name}"
            try:
                yield _import_workflow_module(module_name)
            except Exception:
                _LOG.exception("Failed to import Workflow Runner module %s", module_name)
                continue

def iter_workflow_definitions(
    extra_workflow_roots: Iterable[str | Path] | None = None,
) -> Iterable[object]:
    """
    Yield each workflow definition exported by the configured workflow modules.

    Modules can expose either:
      * WORKFLOWS: an iterable of WorkflowNode instances, or
      * WORKFLOW: a single WorkflowNode instance.
    """
    for module in iter_workflow_modules(extra_workflow_roots):
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
