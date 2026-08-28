from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ...api import get_resource_url
from ...comfy import get_comfy_dir, resolve_filepath
from ...conversion import pil_to_tensor, tensor_to_pil
from ...logic import normalize_output_image
from ...temp_cache import TempFileCache
from ...ui import create_masonry_node
from ..context import clear_editing_context, register_editing_context
from ..file_lock import edit_dataset_lock
from ..ownership import OWNER_CLIENT_ID_KEY, get_owner_client_id, normalize_client_id

__all__ = ["EditingSession", "EditingSessionResult"]

_TRANSIENT_READ_ATTEMPTS = 20

@dataclass
class EditingSessionResult:
    dataset: Dict[str, Any]
    batch_list: List
    image_list: List
    selected_entry: Optional[Dict[str, Any]] = None

@dataclass
class EditingSession:
    node_id: str
    temp_cache: TempFileCache = field(default_factory=TempFileCache)
    owner_client_id: str | None = None

    def __post_init__(self) -> None:
        self.node_id = str(self.node_id)
        self.owner_client_id = normalize_client_id(self.owner_client_id)

    def build_dataset(
        self,
        images: Iterable,
        *,
        filename_prefix: str,
        temp_type: str = "temp",
    ) -> Dict[str, Any]:
        nodes: list[dict] = []
        dataset: dict[str, Any] = {
            "nodes": nodes,
            "lf_node_id": str(self.node_id),
            "prefix": filename_prefix,
        }

        for index, img in enumerate(images):
            pil_image = tensor_to_pil(img)
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix=filename_prefix,
                image=img,
                temp_cache=self.temp_cache,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, temp_type)
            nodes.append(create_masonry_node(filename, url, index))

        return self.bind_dataset_context(dataset, default_status="pending")

    def bind_dataset_context(
        self,
        dataset: Dict[str, Any],
        *,
        default_status: str,
    ) -> Dict[str, Any]:
        """Bind a serialized editor dataset to one fresh, node-owned temp session."""
        context_id = self._build_context_path()
        dataset["lf_node_id"] = str(self.node_id)
        dataset["context_id"] = context_id
        dataset[OWNER_CLIENT_ID_KEY] = self.owner_client_id

        columns = dataset.get("columns")
        if not isinstance(columns, list):
            columns = []
            dataset["columns"] = columns

        path_columns = [
            column
            for column in columns
            if isinstance(column, dict) and column.get("id") == "path"
        ]
        if len(path_columns) > 1:
            raise ValueError("Editing dataset requires exactly one path column.")
        if path_columns:
            path_columns[0]["title"] = context_id
        else:
            columns.insert(0, {"id": "path", "title": context_id})

        status_columns = [
            column
            for column in columns
            if isinstance(column, dict) and column.get("id") == "status"
        ]
        if len(status_columns) > 1:
            raise ValueError("Editing dataset requires exactly one status column.")
        if not status_columns:
            columns.append({"id": "status", "title": default_status})
        elif status_columns[0].get("title") not in {"pending", "completed"}:
            raise ValueError("Editing dataset has an invalid status.")

        selection = dataset.get("selection")
        if isinstance(selection, dict):
            selection["context_id"] = context_id

        return dataset

    def register_context(self, dataset: Dict[str, Any], **context: Any) -> None:
        context_id = dataset["context_id"]
        with edit_dataset_lock(context_id):
            self._write_dataset(dataset)
            registered_context = dict(context)
            registered_context[OWNER_CLIENT_ID_KEY] = self.owner_client_id
            register_editing_context(
                context_id,
                node_id=self.node_id,
                **registered_context,
            )

    def wait_for_completion(self, dataset: Dict[str, Any], *, poll_interval: float = 0.5) -> Dict[str, Any]:
        json_file_path = dataset["context_id"]
        transient_read_failures = 0
        while True:
            try:
                with edit_dataset_lock(json_file_path):
                    with open(json_file_path, "r", encoding="utf-8") as json_file:
                        latest = json.load(json_file)
                transient_read_failures = 0
            except FileNotFoundError as error:
                raise RuntimeError(
                    "Editing session dataset disappeared before completion."
                ) from error
            except (PermissionError, json.JSONDecodeError):
                # Windows can briefly deny a new reader while os.replace swaps
                # the completed session file. A legacy writer may also still be
                # finishing an in-place JSON update. Retry a bounded number of
                # times so a corrupt session cannot strand execution forever.
                transient_read_failures += 1
                if transient_read_failures >= _TRANSIENT_READ_ATTEMPTS:
                    raise
                time.sleep(poll_interval)
                continue

            status_column = next((col for col in latest.get("columns", []) if col.get("id") == "status"), None)
            if status_column and status_column.get("title") == "completed":
                return latest

            time.sleep(poll_interval)

    def cleanup(self, dataset: Dict[str, Any]) -> None:
        self.retire_owned_context(dataset.get("context_id"))

    def retire_owned_context(
        self,
        context_id: object,
        *,
        except_context_id: object = None,
    ) -> bool:
        """Retire only a same-node UUID session under Comfy's current temp root."""
        resolved = self._resolve_owned_context_path(context_id)
        if resolved is None:
            return False
        except_resolved = self._resolve_owned_context_path(except_context_id)
        if except_resolved is not None and os.path.normcase(resolved) == os.path.normcase(except_resolved):
            return False

        with edit_dataset_lock(resolved):
            if os.path.isfile(resolved):
                try:
                    with open(resolved, "r", encoding="utf-8") as json_file:
                        persisted_dataset = json.load(json_file)
                    if not isinstance(persisted_dataset, dict):
                        return False
                    persisted_owner = get_owner_client_id(persisted_dataset)
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    return False
                if (
                    persisted_owner is not None
                    and persisted_owner != self.owner_client_id
                ):
                    return False

            removed = True
            try:
                os.remove(resolved)
            except FileNotFoundError:
                # Already cleaned up or never created; nothing to do.
                pass
            except OSError:
                # Preserve the file as diagnostic/recovery residue, but revoke
                # its live model/conditioning authority at retirement.
                removed = False
            clear_editing_context(resolved)
        return removed

    def collect_results(self, dataset: Dict[str, Any]) -> EditingSessionResult:
        nodes = dataset.get("nodes")
        if not isinstance(nodes, list):
            raise ValueError("Editing dataset nodes must be a list.")

        edited_images = []
        selected_entry = self._resolve_selected_entry(dataset)

        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                raise ValueError(
                    f"Editing dataset entry {index} must be an object."
                )
            cells = node.get("cells")
            if not isinstance(cells, dict):
                raise ValueError(
                    f"Editing dataset entry {index} has invalid cells."
                )
            lf_image = cells.get("lfImage")
            if not isinstance(lf_image, dict):
                lf_image = {}
            image_url = lf_image.get("lfValue") or lf_image.get("value")
            if not isinstance(image_url, str) or not image_url.strip():
                raise ValueError(
                    f"Editing dataset entry {index} is missing an image URL."
                )

            try:
                image_path = self._resolve_image_path(image_url)
                pil_image = self._load_pil(image_path)
            except (FileNotFoundError, OSError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Editing dataset entry {index} could not be loaded: {error}"
                ) from error

            edited_images.append(pil_to_tensor(pil_image))

        if len(edited_images) != len(nodes):
            raise ValueError(
                "Editing dataset image cardinality changed during collection."
            )

        batch_list, image_list = self._to_normalized_lists(edited_images)
        return EditingSessionResult(
            dataset=dataset,
            batch_list=batch_list,
            image_list=image_list,
            selected_entry=selected_entry,
        )

    # region internal helpers
    def _build_context_path(self) -> str:
        unique_suffix = uuid.uuid4().hex
        return os.path.join(
            get_comfy_dir("temp"),
            f"{self.node_id}_{unique_suffix}_edit_dataset.json",
        )

    def _resolve_owned_context_path(self, context_id: object) -> str | None:
        if not isinstance(context_id, str) or not context_id.strip():
            return None
        temp_root = os.path.realpath(os.path.abspath(get_comfy_dir("temp")))
        candidate = os.path.realpath(os.path.abspath(context_id))
        try:
            if os.path.commonpath((os.path.normcase(temp_root), os.path.normcase(candidate))) != os.path.normcase(temp_root):
                return None
        except ValueError:
            return None
        expected_name = re.compile(
            rf"^{re.escape(str(self.node_id))}_[0-9a-fA-F]{{32}}_edit_dataset\.json$"
        )
        return candidate if expected_name.fullmatch(os.path.basename(candidate)) else None

    def _write_dataset(self, dataset: Dict[str, Any]) -> None:
        with edit_dataset_lock(dataset["context_id"]):
            with open(dataset["context_id"], "w", encoding="utf-8") as json_file:
                json.dump(dataset, json_file, ensure_ascii=False, indent=4)

    def _load_pil(self, path: str):
        from PIL import Image

        with Image.open(path) as img:
            mode = "RGBA" if "A" in img.getbands() else "RGB"
            return img.convert(mode).copy()

    def _resolve_image_path(self, url: str) -> str:
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        filename = query_params.get("filename", [None])[0]
        file_type = query_params.get("type", [None])[0]
        subfolder = query_params.get("subfolder", [None])[0]

        if not filename or not file_type:
            raise ValueError("Image URL is missing filename or type.")

        return os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

    def _resolve_selected_entry(self, dataset: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        columns = dataset.get("columns", [])
        if not isinstance(columns, list):
            return None
        for column in columns:
            if (
                isinstance(column, dict)
                and column.get("id") == "selected"
                and isinstance(column.get("title"), dict)
            ):
                return column["title"]
        return None

    def _to_normalized_lists(self, images: Iterable) -> Tuple[List, List]:
        if not images:
            return [], []

        batch_list, image_list = normalize_output_image(images)
        return list(batch_list), list(image_list)

    # endregion
