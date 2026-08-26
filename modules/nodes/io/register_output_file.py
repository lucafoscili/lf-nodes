"""Register an existing output-root file in ComfyUI's durable history."""

from __future__ import annotations

import unicodedata
from pathlib import Path, PureWindowsPath
from typing import Any

import folder_paths

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync


OUTPUT_FILE_RECEIPT_SCHEMA = "lf.output_file.receipt.v1"
_MAX_HISTORY_PATH_LENGTH = 1024


def _unwrap_path(value: Any) -> str:
    while isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError("relative_path must identify exactly one output file.")
        value = value[0]
    if not isinstance(value, str) or not value:
        raise ValueError("relative_path must be a non-empty string.")
    return value


def _normalize_relative_path(value: Any) -> str:
    raw = _unwrap_path(value)
    if any(unicodedata.category(character) == "Cc" for character in raw):
        raise ValueError("relative_path cannot contain control characters.")

    portable = raw.replace("\\", "/")
    windows_path = PureWindowsPath(raw)
    if portable.startswith("/") or windows_path.is_absolute() or windows_path.drive:
        raise ValueError(
            "relative_path must be relative to the ComfyUI output directory."
        )

    raw_parts = portable.split("/")
    if any(
        part == ".." or (part.startswith("..") and not part[2:].strip(" ."))
        for part in raw_parts
    ):
        raise ValueError("relative_path cannot contain parent traversal.")

    parts = [part for part in raw_parts if part not in {"", "."}]
    if not parts:
        raise ValueError("relative_path must identify a file.")
    if any(":" in part for part in parts):
        raise ValueError("relative_path cannot contain a drive or alternate stream.")

    normalized = "/".join(parts)
    if len(normalized) > _MAX_HISTORY_PATH_LENGTH:
        raise ValueError("relative_path is too long for ComfyUI history.")
    return normalized


def _resolve_output_file(value: Any) -> tuple[str, int]:
    normalized = _normalize_relative_path(value)
    try:
        output_root = Path(folder_paths.get_output_directory()).resolve(strict=True)
    except (OSError, RuntimeError, TypeError):
        raise ValueError("The ComfyUI output directory is unavailable.") from None
    if not output_root.is_dir():
        raise ValueError("The ComfyUI output directory is unavailable.")

    candidate = output_root.joinpath(*normalized.split("/"))
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        raise ValueError("relative_path does not identify an existing output file.") from None

    try:
        canonical_relative = resolved.relative_to(output_root).as_posix()
    except ValueError:
        raise ValueError(
            "relative_path resolves outside the ComfyUI output directory."
        ) from None

    if not resolved.is_file():
        raise ValueError("relative_path must identify a regular output file.")
    try:
        byte_length = resolved.stat().st_size
    except OSError:
        raise ValueError("The output file could not be inspected.") from None
    return canonical_relative, byte_length


class LF_RegisterOutputFile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "relative_path": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": (
                            "Existing file path relative to ComfyUI's output directory. "
                            "Use this after a third-party node writes a file without "
                            "publishing it to history."
                        ),
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Normalized path relative to the ComfyUI output directory.",
    )
    RETURN_NAMES = ("relative_path",)
    RETURN_TYPES = (Input.STRING,)

    def on_exec(self, relative_path: str, **kwargs: dict):
        normalized, byte_length = _resolve_output_file(relative_path)
        receipt = {
            "schema": OUTPUT_FILE_RECEIPT_SCHEMA,
            "file_name": normalized,
            "storage_type": "output",
            "byte_length": byte_length,
        }
        file_node = {
            "description": f"{byte_length} bytes",
            "icon": "file",
            "id": normalized,
            "value": normalized,
        }
        dataset = {
            "nodes": [
                {
                    "children": [file_node],
                    "icon": "check",
                    "id": "root",
                    "value": "Output file registered.",
                }
            ]
        }
        lf_output = {
            "dataset": dataset,
            "file_names": [normalized],
            "receipt": receipt,
        }

        safe_send_sync(
            "registeroutputfile",
            {"dataset": dataset},
            kwargs.get("node_id"),
        )
        return {
            "ui": {"lf_output": [lf_output]},
            "result": (normalized,),
        }


NODE_CLASS_MAPPINGS = {
    "LF_RegisterOutputFile": LF_RegisterOutputFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_RegisterOutputFile": "Register output file",
}
