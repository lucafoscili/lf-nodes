from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ...api import get_resource_url
from ...comfy import get_comfy_dir, resolve_filepath
from ...conversion import pil_to_tensor, tensor_to_pil
from ...logic import normalize_output_image
from ...temp_cache import TempFileCache
from ...ui import create_masonry_node
from ..context import clear_editing_context, register_editing_context

__all__ = ["EditingSession", "EditingSessionResult"]

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

    def build_dataset(
        self,
        images: Iterable,
        *,
        filename_prefix: str,
        temp_type: str = "temp",
    ) -> Dict[str, Any]:
        nodes: list[dict] = []
        dataset: dict[str, Any] = {"nodes": nodes}

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

        dataset["context_id"] = self._build_context_path()
        dataset.setdefault("columns", []).extend(
            (
                {"id": "path", "title": dataset["context_id"]},
                {"id": "status", "title": "pending"},
            )
        )
        return dataset

    def register_context(self, dataset: Dict[str, Any], **context: Any) -> None:
        register_editing_context(dataset["context_id"], **context)
        self._write_dataset(dataset)

    def wait_for_completion(self, dataset: Dict[str, Any], *, poll_interval: float = 0.5) -> Dict[str, Any]:
        json_file_path = dataset["context_id"]
        while True:
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                latest = json.load(json_file)

            status_column = next((col for col in latest.get("columns", []) if col.get("id") == "status"), None)
            if status_column and status_column.get("title") == "completed":
                return latest

            time.sleep(poll_interval)

    def cleanup(self, dataset: Dict[str, Any]) -> None:
        clear_editing_context(dataset.get("context_id"))

    def collect_results(self, dataset: Dict[str, Any]) -> EditingSessionResult:
        edited_images = []
        selected_entry = self._resolve_selected_entry(dataset)

        for node in dataset.get("nodes", []):
            lf_image = node.get("cells", {}).get("lfImage") or {}
            image_url = lf_image.get("lfValue") or lf_image.get("value")
            if not image_url:
                continue

            try:
                image_path = self._resolve_image_path(image_url)
                pil_image = self._load_pil(image_path)
            except (FileNotFoundError, OSError):
                continue

            edited_images.append(pil_to_tensor(pil_image))

        batch_list, image_list = self._to_normalized_lists(edited_images)
        return EditingSessionResult(
            dataset=dataset,
            batch_list=batch_list,
            image_list=image_list,
            selected_entry=selected_entry,
        )

    # region internal helpers
    def _build_context_path(self) -> str:
        return os.path.join(get_comfy_dir("temp"), f"{self.node_id}_edit_dataset.json")

    def _write_dataset(self, dataset: Dict[str, Any]) -> None:
        with open(dataset["context_id"], "w", encoding="utf-8") as json_file:
            json.dump(dataset, json_file, ensure_ascii=False, indent=4)

    def _load_pil(self, path: str):
        from PIL import Image

        with Image.open(path) as img:
            return img.convert("RGB").copy()

    def _resolve_image_path(self, url: str) -> str:
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        filename = query_params.get("filename", [None])[0]
        file_type = query_params.get("type", [None])[0]
        subfolder = query_params.get("subfolder", [None])[0]

        return os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

    def _resolve_selected_entry(self, dataset: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        columns = dataset.get("columns", [])
        for column in columns:
            if column.get("id") == "selected" and isinstance(column.get("title"), dict):
                return column["title"]
        return None

    def _to_normalized_lists(self, images: Iterable) -> Tuple[List, List]:
        if not images:
            return [], []

        batch_list, image_list = normalize_output_image(images)
        return list(batch_list), list(image_list)

    # endregion
