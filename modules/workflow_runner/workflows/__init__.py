from importlib import import_module
import logging
import os
from pathlib import Path
from types import ModuleType
from typing import Iterable, Iterator, Sequence
import pkgutil

_LOG = logging.getLogger(__name__)

_SHIPPED_ORIGIN = "shipped"
_SHIPPED_COLLECTION = "LF Nodes"
_CUSTOM_ORIGIN = "custom"
_CUSTOM_COLLECTION = "Custom"
_ORIGIN_ATTR = "__lf_workflow_origin__"
_COLLECTION_ATTR = "__lf_workflow_collection__"


class _WorkflowDefinitionWithProvenance:
    """Attach trusted module provenance to immutable duck-typed definitions."""

    __slots__ = ("_definition", "origin", "collection")

    def __init__(self, definition: object, origin: str, collection: str) -> None:
        self._definition = definition
        self.origin = origin
        self.collection = collection

    def __getattr__(self, name: str) -> object:
        return getattr(self._definition, name)

_WORKFLOW_MODULES: Sequence[str] = (
    "caption_image_vision",
    "compare_images",
    "image_detail_4k",
    "image_sheet",
    "image_to_dds",
    "image_to_svg",
    "krea2",
    "load_metadata",
    "minimax_h3",
    "remove_bg",
    "simple_chat",
    "sort_json_keys",
    "svg_generation_gemini",
    "t2i_15_lcm",
    "t2i_illustrious_xl",
    "trellis2",
    "triposplat",
    "ace_step_remix",
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


def _extra_workflow_groups_from_settings() -> tuple[str, ...]:
    from ..config import get_settings

    configured = getattr(
        get_settings(),
        "WORKFLOW_RUNNER_EXTRA_WORKFLOW_GROUPS",
        (),
    )
    return tuple(configured or ())


def _normalize_collection_label(value: object) -> str:
    label = " ".join(str(value or "").split())
    if not label or len(label) > 80 or any(ord(char) < 32 for char in label):
        return _CUSTOM_COLLECTION
    return label


def _resolved_root_groups(
    raw_roots: Iterable[str | Path],
    raw_groups: Sequence[str],
) -> tuple[tuple[Path, ...], tuple[str, ...]]:
    raw_root_list = tuple(raw_roots)
    resolved_roots = _resolve_extra_workflow_roots(raw_root_list)
    groups_by_root: dict[Path, str] = {}
    allowed = set(resolved_roots)
    for index, raw_root in enumerate(raw_root_list):
        candidate = Path(os.path.expandvars(str(raw_root))).expanduser()
        if not candidate.is_absolute():
            continue
        try:
            resolved = candidate.resolve(strict=True)
        except (OSError, RuntimeError):
            continue
        if resolved not in allowed or resolved in groups_by_root:
            continue
        raw_group = raw_groups[index] if index < len(raw_groups) else ""
        groups_by_root[resolved] = _normalize_collection_label(raw_group)
    return resolved_roots, tuple(groups_by_root[root] for root in resolved_roots)


def _module_collection(
    module: ModuleType,
    roots: Sequence[Path],
    groups: Sequence[str],
) -> str:
    module_file = getattr(module, "__file__", None)
    if not module_file:
        return _CUSTOM_COLLECTION
    try:
        module_path = Path(module_file).resolve().parent
    except (OSError, RuntimeError):
        return _CUSTOM_COLLECTION

    matches = [
        (index, root)
        for index, root in enumerate(roots)
        if module_path == root or root in module_path.parents
    ]
    if matches:
        # Nested custom roots are valid. Attribute a module to the most-specific
        # configured root instead of whichever containing parent appeared first.
        index, _root = max(matches, key=lambda match: len(match[1].parts))
        raw_group = groups[index] if index < len(groups) else ""
        return _normalize_collection_label(raw_group)
    return _CUSTOM_COLLECTION


def _mark_module(module: ModuleType, origin: str, collection: str) -> ModuleType:
    setattr(module, _ORIGIN_ATTR, origin)
    setattr(module, _COLLECTION_ATTR, collection)
    return module


def _definition_with_provenance(
    definition: object,
    origin: str,
    collection: str,
) -> object:
    try:
        setattr(definition, "origin", origin)
        setattr(definition, "collection", collection)
        if (
            getattr(definition, "origin", None) == origin
            and getattr(definition, "collection", None) == collection
        ):
            return definition
    except (AttributeError, TypeError):
        pass

    return _WorkflowDefinitionWithProvenance(definition, origin, collection)


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
    extra_workflow_groups: Iterable[str] | None = None,
) -> Iterator[ModuleType]:
    for module_name in _WORKFLOW_MODULES:
        yield _mark_module(
            _import_workflow_module(module_name),
            _SHIPPED_ORIGIN,
            _SHIPPED_COLLECTION,
        )

    configured_roots = (
        _extra_workflow_roots_from_settings()
        if extra_workflow_roots is None
        else extra_workflow_roots
    )
    configured_groups = (
        _extra_workflow_groups_from_settings()
        if extra_workflow_groups is None and extra_workflow_roots is None
        else tuple(extra_workflow_groups or ())
    )
    resolved_roots, resolved_groups = _resolved_root_groups(
        configured_roots,
        tuple(configured_groups),
    )
    custom_pkg = _configure_custom_package_paths(resolved_roots)

    if custom_pkg is not None and hasattr(custom_pkg, "__path__"):
        for name in _discover_custom_module_names(custom_pkg):
            module_name = f"custom.{name}"
            try:
                module = _import_workflow_module(module_name)
                yield _mark_module(
                    module,
                    _CUSTOM_ORIGIN,
                    _module_collection(module, resolved_roots, resolved_groups),
                )
            except Exception:
                _LOG.exception("Failed to import Workflow Runner module %s", module_name)
                continue

def iter_workflow_definitions(
    extra_workflow_roots: Iterable[str | Path] | None = None,
    extra_workflow_groups: Iterable[str] | None = None,
) -> Iterable[object]:
    """
    Yield each workflow definition exported by the configured workflow modules.

    Modules can expose either:
      * WORKFLOWS: an iterable of WorkflowNode instances, or
      * WORKFLOW: a single WorkflowNode instance.
    """
    for module in iter_workflow_modules(extra_workflow_roots, extra_workflow_groups):
        origin = getattr(module, _ORIGIN_ATTR, _SHIPPED_ORIGIN)
        collection = getattr(module, _COLLECTION_ATTR, _SHIPPED_COLLECTION)
        definitions = getattr(module, "WORKFLOWS", None)
        if definitions is None:
            single_definition = getattr(module, "WORKFLOW", None)
            definitions = () if single_definition is None else (single_definition,)

        if isinstance(definitions, (list, tuple, set)):
            for definition in definitions:
                if definition is not None:
                    yield _definition_with_provenance(
                        definition,
                        origin,
                        collection,
                    )
        elif definitions is not None:
            yield _definition_with_provenance(
                definitions,
                origin,
                collection,
            )
# endregion
