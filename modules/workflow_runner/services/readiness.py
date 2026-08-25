"""Lightweight, non-executing readiness checks for Runner workflows.

The catalogue check is deliberately narrow. It verifies the default prompt's
node types against ComfyUI's already-loaded node registry and checks literal
file selections for a small set of known Core loader inputs. It never loads a
model, downloads anything, or treats an unavailable scanner as proof that a
workflow cannot run.
"""

from __future__ import annotations

import importlib
import os

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


READINESS_READY = "ready"
READINESS_WARNING = "warning"
READINESS_SETUP_REQUIRED = "setup_required"

MAX_READINESS_ISSUES = 8
_MAX_LABEL_LENGTH = 120


@dataclass(frozen=True, slots=True)
class _LoaderAsset:
    input_name: str
    folder_category: str
    label: str


# These mappings mirror filename-backed loaders shipped by ComfyUI Core (and
# its bundled extras). Unknown/custom loaders are intentionally not guessed.
_CORE_LOADER_ASSETS: dict[str, tuple[_LoaderAsset, ...]] = {
    "CheckpointLoader": (_LoaderAsset("ckpt_name", "checkpoints", "checkpoint"),),
    "CheckpointLoaderSimple": (
        _LoaderAsset("ckpt_name", "checkpoints", "checkpoint"),
    ),
    "unCLIPCheckpointLoader": (
        _LoaderAsset("ckpt_name", "checkpoints", "checkpoint"),
    ),
    "UNETLoader": (
        _LoaderAsset("unet_name", "diffusion_models", "diffusion model"),
    ),
    "CLIPLoader": (
        _LoaderAsset("clip_name", "text_encoders", "text encoder"),
    ),
    "DualCLIPLoader": (
        _LoaderAsset("clip_name1", "text_encoders", "text encoder"),
        _LoaderAsset("clip_name2", "text_encoders", "text encoder"),
    ),
    "TripleCLIPLoader": (
        _LoaderAsset("clip_name1", "text_encoders", "text encoder"),
        _LoaderAsset("clip_name2", "text_encoders", "text encoder"),
        _LoaderAsset("clip_name3", "text_encoders", "text encoder"),
    ),
    "QuadrupleCLIPLoader": (
        _LoaderAsset("clip_name1", "text_encoders", "text encoder"),
        _LoaderAsset("clip_name2", "text_encoders", "text encoder"),
        _LoaderAsset("clip_name3", "text_encoders", "text encoder"),
        _LoaderAsset("clip_name4", "text_encoders", "text encoder"),
    ),
    "VAELoader": (_LoaderAsset("vae_name", "vae", "VAE"),),
    "LoraLoader": (_LoaderAsset("lora_name", "loras", "LoRA"),),
    "LoraLoaderModelOnly": (_LoaderAsset("lora_name", "loras", "LoRA"),),
    "ControlNetLoader": (
        _LoaderAsset("control_net_name", "controlnet", "ControlNet"),
    ),
    "DiffControlNetLoader": (
        _LoaderAsset("control_net_name", "controlnet", "ControlNet"),
    ),
    "CLIPVisionLoader": (
        _LoaderAsset("clip_name", "clip_vision", "CLIP Vision model"),
    ),
    "StyleModelLoader": (
        _LoaderAsset("style_model_name", "style_models", "style model"),
    ),
    "GLIGENLoader": (_LoaderAsset("gligen_name", "gligen", "GLIGEN model"),),
    "UpscaleModelLoader": (
        _LoaderAsset("model_name", "upscale_models", "upscale model"),
    ),
}

# These are virtual Core VAE choices rather than files in models/vae.
_VIRTUAL_VAE_NAMES = {
    "pixel_space",
    "taesd",
    "taesdxl",
    "taesd3",
    "taef1",
    "taef2",
}


@dataclass(frozen=True, slots=True)
class _Issue:
    code: str
    message: str
    blocking: bool = False

    def public(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def _safe_label(value: object) -> str:
    text = " ".join(str(value).split())
    if len(text) > _MAX_LABEL_LENGTH:
        return f"{text[: _MAX_LABEL_LENGTH - 1]}…"
    return text


def _normalized_filename(value: str) -> str:
    # Comfy may return host-native separators while a portable workflow stores
    # forward slashes.
    normalized = value.replace("\\", "/")
    return normalized.casefold() if os.name == "nt" else normalized


def _cell_exposes_asset_filename(cell: object, filename: str) -> bool:
    """Return whether a form cell directly offers one loader filename.

    Sharing a loader node is not sufficient evidence: a form may expose only
    that loader's strength or another numeric setting while the file selection
    remains immutable.  Runner cells publish their effective default through
    ``lfValue`` and select alternatives through ``lfDataset``.
    """

    props = getattr(cell, "props", None)
    if not isinstance(props, Mapping):
        return False

    expected = _normalized_filename(filename)
    default = props.get("lfValue")
    if isinstance(default, str) and _normalized_filename(default.strip()) == expected:
        return True

    dataset = props.get("lfDataset")
    nodes = dataset.get("nodes") if isinstance(dataset, Mapping) else None
    if not isinstance(nodes, Iterable) or isinstance(nodes, (str, bytes, Mapping)):
        return False
    for option in nodes:
        if not isinstance(option, Mapping):
            continue
        # Mirror the browser select dispatcher: workflowValue wins, followed
        # by value and then id. A display label that happens to look like a
        # filename is not proof that the submitted value selects that file.
        value = option.get("workflowValue")
        if value is None:
            value = option.get("value")
        if value is None:
            value = option.get("id")
        if isinstance(value, str) and _normalized_filename(value.strip()) == expected:
            return True
    return False


def _load_node_class_mappings() -> Mapping[str, object]:
    nodes_module = importlib.import_module("nodes")
    mappings = getattr(nodes_module, "NODE_CLASS_MAPPINGS")
    if not isinstance(mappings, Mapping):
        raise TypeError("NODE_CLASS_MAPPINGS is unavailable")
    return mappings


def _load_model_filenames(folder_category: str) -> Iterable[str]:
    folder_paths = importlib.import_module("folder_paths")
    get_filename_list = getattr(folder_paths, "get_filename_list")
    filenames = get_filename_list(folder_category)
    if isinstance(filenames, (str, bytes)) or not isinstance(filenames, Iterable):
        raise TypeError("model filename scanner returned an invalid result")
    return filenames


class WorkflowReadinessScanner:
    """One catalogue request's cached view of lightweight host readiness."""

    def __init__(
        self,
        *,
        node_mapping_loader: Callable[[], Mapping[str, object]] | None = None,
        model_filename_loader: Callable[[str], Iterable[str]] | None = None,
    ) -> None:
        self._node_mapping_loader = node_mapping_loader or _load_node_class_mappings
        self._model_filename_loader = model_filename_loader or _load_model_filenames
        self._node_types: frozenset[str] | None = None
        self._node_scan_attempted = False
        self._model_files: dict[str, frozenset[str] | None] = {}

    def node_types(self) -> frozenset[str] | None:
        if self._node_scan_attempted:
            return self._node_types

        self._node_scan_attempted = True
        try:
            mappings = self._node_mapping_loader()
            self._node_types = frozenset(
                key for key in mappings if isinstance(key, str) and key
            )
        except Exception:
            self._node_types = None
        return self._node_types

    def model_filenames(self, folder_category: str) -> frozenset[str] | None:
        if folder_category in self._model_files:
            return self._model_files[folder_category]

        try:
            filenames = self._model_filename_loader(folder_category)
            normalized = frozenset(
                _normalized_filename(filename)
                for filename in filenames
                if isinstance(filename, str) and filename
            )
        except Exception:
            normalized = None
        self._model_files[folder_category] = normalized
        return normalized


def _bounded_public_result(issues: list[_Issue]) -> dict[str, object]:
    blocking = any(issue.blocking for issue in issues)
    if blocking:
        status = READINESS_SETUP_REQUIRED
    elif issues:
        status = READINESS_WARNING
    else:
        status = READINESS_READY

    # The frontend intentionally shows the first issue in its compact notice.
    # Keep the original order within each severity while ensuring a proven
    # blocker is never hidden behind an earlier scanner uncertainty.
    public_issues = [issue for issue in issues if issue.blocking] + [
        issue for issue in issues if not issue.blocking
    ]
    if len(public_issues) > MAX_READINESS_ISSUES:
        omitted = len(public_issues) - (MAX_READINESS_ISSUES - 1)
        public_issues = public_issues[: MAX_READINESS_ISSUES - 1] + [
            _Issue(
                "readiness_issues_truncated",
                f"{omitted} additional readiness issue(s) were omitted.",
                blocking=blocking,
            )
        ]

    return {
        "status": status,
        "issues": [issue.public() for issue in public_issues],
    }


def _missing_workflow_result(path: object) -> dict[str, object]:
    try:
        filename = Path(path).name if path is not None else "workflow definition"
    except (TypeError, ValueError):
        filename = "workflow definition"
    return _bounded_public_result(
        [
            _Issue(
                "workflow_file_missing",
                f"Workflow definition file is missing: {_safe_label(filename)}.",
                blocking=True,
            )
        ]
    )


def evaluate_workflow_readiness(
    definition: Any,
    *,
    scanner: WorkflowReadinessScanner | None = None,
) -> dict[str, object]:
    """Evaluate the runnable default graph without executing or loading it."""

    workflow_path = getattr(definition, "workflow_path", None)
    if workflow_path is None:
        return _missing_workflow_result(workflow_path)

    try:
        path = Path(workflow_path)
    except (TypeError, ValueError):
        return _missing_workflow_result(workflow_path)
    if not path.is_file():
        return _missing_workflow_result(path)

    try:
        prompt = definition.load_prompt()
    except Exception:
        return _bounded_public_result(
            [
                _Issue(
                    "workflow_file_unreadable",
                    f"Workflow definition could not be read: {_safe_label(path.name)}.",
                    blocking=True,
                )
            ]
        )

    if not isinstance(prompt, Mapping) or not prompt:
        return _bounded_public_result(
            [
                _Issue(
                    "workflow_prompt_empty",
                    "Workflow definition does not contain an executable prompt.",
                    blocking=True,
                )
            ]
        )

    active_scanner = scanner or WorkflowReadinessScanner()
    issues: list[_Issue] = []

    available_node_types = active_scanner.node_types()
    if available_node_types is None:
        issues.append(
            _Issue(
                "node_scanner_unavailable",
                "Installed node types could not be checked; readiness is uncertain.",
            )
        )

    prompt_nodes: list[tuple[str, str, Mapping[str, Any]]] = []
    invalid_nodes = 0
    for raw_node_id, raw_node in prompt.items():
        if not isinstance(raw_node, Mapping):
            invalid_nodes += 1
            continue
        class_type = raw_node.get("class_type")
        if not isinstance(class_type, str) or not class_type.strip():
            invalid_nodes += 1
            continue
        prompt_nodes.append((str(raw_node_id), class_type, raw_node))

    if invalid_nodes:
        issues.append(
            _Issue(
                "workflow_node_invalid",
                f"Workflow contains {invalid_nodes} node(s) without a valid type.",
                blocking=True,
            )
        )

    if available_node_types is not None:
        required_types = sorted({class_type for _node_id, class_type, _node in prompt_nodes})
        for class_type in required_types:
            if class_type not in available_node_types:
                issues.append(
                    _Issue(
                        "node_missing",
                        f"Required node type is not installed: {_safe_label(class_type)}.",
                        blocking=True,
                    )
                )

    unavailable_model_categories: set[str] = set()
    missing_models: set[tuple[str, str, str]] = set()
    configurable_missing_models: set[tuple[str, str, str]] = set()
    try:
        configurable_cells_by_node: dict[str, list[object]] = {}
        for cell in getattr(definition, "inputs", ()):
            cell_node_id = getattr(cell, "node_id", None)
            if cell_node_id is not None:
                configurable_cells_by_node.setdefault(str(cell_node_id), []).append(cell)
    except (TypeError, ValueError):
        configurable_cells_by_node = {}

    for node_id, class_type, raw_node in prompt_nodes:
        loader_assets = _CORE_LOADER_ASSETS.get(class_type, ())
        inputs = raw_node.get("inputs")
        if not loader_assets or not isinstance(inputs, Mapping):
            continue

        for asset in loader_assets:
            filename = inputs.get(asset.input_name)
            # A link or computed value is not a provable missing local file.
            if not isinstance(filename, str) or not filename.strip():
                continue
            filename = filename.strip()
            if asset.folder_category == "vae" and filename in _VIRTUAL_VAE_NAMES:
                continue

            available_files = active_scanner.model_filenames(asset.folder_category)
            if available_files is None:
                unavailable_model_categories.add(asset.folder_category)
                continue
            if _normalized_filename(filename) not in available_files:
                missing = (asset.folder_category, asset.label, filename)
                if any(
                    _cell_exposes_asset_filename(cell, filename)
                    for cell in configurable_cells_by_node.get(node_id, ())
                ):
                    configurable_missing_models.add(missing)
                else:
                    missing_models.add(missing)

    for folder_category in sorted(unavailable_model_categories):
        issues.append(
            _Issue(
                "model_scanner_unavailable",
                "Installed files could not be checked for model category "
                f"{_safe_label(folder_category)}; readiness is uncertain.",
            )
        )

    for _category, label, filename in sorted(
        missing_models,
        key=lambda item: (item[0], _normalized_filename(item[2])),
    ):
        issues.append(
            _Issue(
                "model_missing",
                f"Required {label} file is not installed: {_safe_label(filename)}.",
                blocking=True,
            )
        )

    for _category, label, filename in sorted(
        configurable_missing_models - missing_models,
        key=lambda item: (item[0], _normalized_filename(item[2])),
    ):
        issues.append(
            _Issue(
                "default_model_missing",
                f"Default {label} file is not installed: {_safe_label(filename)}. "
                "Choose an installed option before running.",
            )
        )

    return _bounded_public_result(issues)


__all__ = [
    "MAX_READINESS_ISSUES",
    "READINESS_READY",
    "READINESS_SETUP_REQUIRED",
    "READINESS_WARNING",
    "WorkflowReadinessScanner",
    "evaluate_workflow_readiness",
]
