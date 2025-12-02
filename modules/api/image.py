import asyncio
import folder_paths
import hashlib
import json
import logging
import os
import time
import torch

from aiohttp import web
from PIL import Image
from typing import List, Optional, Tuple

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX, IMAGE_FILE_EXTENSIONS
from ..utils.filters.processors import UnknownFilterError, process_filter
from ..utils.helpers.api import get_resource_url, resolve_url
from ..utils.helpers.comfy import (
    ensure_external_preview,
    get_comfy_dir,
    resolve_filepath,
    resolve_input_directory_path,
)
from ..utils.helpers.conversion import pil_to_tensor, tensor_to_pil
from ..utils.helpers.logic import sanitize_filename
from ..utils.helpers.ui import create_masonry_node

# region constants
TREE_COLUMNS = [
    {"id": "name", "title": "Name"},
    {"id": "items", "title": "Items"},
    {"id": "type", "title": "Type"},
]
MAX_TREE_CHILDREN = 500
# endregion

# region get-image
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-image")
async def get_images_in_directory(request):
    try:
        r: dict = await request.post()

        raw_directory: str = r.get("directory")
        images_dir, resolved_directory, is_external = resolve_input_directory_path(raw_directory)
        if images_dir is None or not os.path.exists(images_dir):
            return web.Response(status=404, text="Directory not found.")

        navigation_directory = _build_navigation_directory(
            raw_directory,
            images_dir,
            resolved_directory,
            is_external=is_external,
        )

        dataset = _build_image_dataset(
            images_dir,
            resolved_directory,
            navigation_directory,
            is_external=is_external,
        )

        return web.json_response(
            {
                "status": "success",
                "data": dataset,
            },
            status=200,
        )

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")

# region explore-filesystem
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/explore-filesystem")
async def explore_filesystem(request):
    try:
        r: dict = await request.post()

        raw_directory: str = r.get("directory")
        scope: str = (r.get("scope") or "all").lower()
        node_path: Optional[str] = r.get("node")

        if scope == "roots":
            return web.json_response(
                {
                    "status": "success",
                    "data": {
                        "dataset": None,
                        "tree": _build_root_tree_dataset(),
                    },
                },
                status=200,
            )

        images_dir, resolved_directory, is_external = resolve_input_directory_path(raw_directory)
        if images_dir is None or not os.path.exists(images_dir):
            return web.Response(status=404, text="Directory not found.")

        navigation_directory = _build_navigation_directory(
            raw_directory,
            images_dir,
            resolved_directory,
            is_external=is_external,
        )

        include_dataset = scope in {"all", "dataset"}
        include_tree = scope in {"all", "tree"}

        dataset = None
        if include_dataset:
            dataset = _build_image_dataset(
                images_dir,
                resolved_directory,
                navigation_directory,
                is_external=is_external,
            )

        tree_dataset = None
        if include_tree:
            target_path = images_dir
            base_for_tree = images_dir

            if node_path:
                candidate_path = os.path.abspath(node_path)
                if not os.path.isdir(candidate_path):
                    return web.Response(status=404, text="Node not found.")

                if _validate_tree_request(images_dir, candidate_path):
                    target_path = candidate_path
                    base_for_tree = images_dir
                else:
                    target_path = candidate_path
                    base_for_tree = candidate_path

            tree_dataset = _build_tree_dataset(
                base_for_tree,
                target_path,
                navigation_directory,
                include_root=(not node_path and target_path == images_dir and scope == "all"),
            )

        return web.json_response(
            {
                "status": "success",
                "data": {
                    "dataset": dataset,
                    "tree": tree_dataset,
                },
            },
            status=200,
        )

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region process-image
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/process-image")
async def process_image(request):
    try:
        r: dict = await request.post()

        api_url: str = r.get("url")
        filter_type: str = r.get("type")
        settings_raw = r.get("settings") or "{}"
        settings: dict = json.loads(settings_raw)

        filename, file_type, subfolder = resolve_url(api_url)

        if not filename or not file_type:
            return web.Response(status=400, text="Missing required URL parameters.")

        images_dir = os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

        if not os.path.exists(images_dir):
            return web.Response(status=404, text="Image not found.")

        img_tensor = _load_image_tensor(images_dir)

        try:
            # Offload so event loop remains responsive for WebSocket progress events.
            processed_tensor, extra_payload = await asyncio.to_thread(
                process_filter,
                filter_type,
                img_tensor,
                settings,
            )
        except UnknownFilterError as exc:
            return web.Response(status=400, text=str(exc))

        save_type: str = str(settings.get("resource_type") or settings.get("output_type") or "temp")
        base_output_path = get_comfy_dir(save_type)

        custom_subfolder_raw = settings.get("subfolder")
        if isinstance(custom_subfolder_raw, str) and custom_subfolder_raw.strip():
            normalized_subfolder = os.path.normpath(custom_subfolder_raw.strip()).strip("\\/")
            if normalized_subfolder.startswith(".."):
                return web.Response(status=400, text="Invalid subfolder path.")
        else:
            normalized_subfolder = ""

        filename_prefix_override = settings.get("filename_prefix")
        if isinstance(filename_prefix_override, str) and filename_prefix_override.strip():
            filename_prefix_value = filename_prefix_override.strip()
        else:
            filename_prefix_value = filter_type

        custom_filename_raw = settings.get("filename")
        if isinstance(custom_filename_raw, str) and custom_filename_raw.strip():
            sanitized_name = sanitize_filename(custom_filename_raw)
            if sanitized_name is None:
                return web.Response(status=400, text="Invalid filename provided.")

            filename_value = sanitized_name
            _, ext = os.path.splitext(filename_value)

            output_folder = os.path.join(base_output_path, normalized_subfolder) if normalized_subfolder else base_output_path
            os.makedirs(output_folder, exist_ok=True)

            output_file = os.path.join(output_folder, filename_value)
            output_folder_abs = os.path.abspath(output_folder)
            output_file_abs = os.path.abspath(output_file)
            if os.path.commonpath([output_folder_abs, output_file_abs]) != output_folder_abs:
                return web.Response(status=400, text="Filename resolves outside of the target directory.")

            final_subfolder = normalized_subfolder.replace("\\", "/") if normalized_subfolder else ""
        else:
            prefixed_name = os.path.join(normalized_subfolder, filename_prefix_value) if normalized_subfolder else filename_prefix_value
            output_file, final_subfolder_raw, filename_value = resolve_filepath(
                filename_prefix=prefixed_name,
                base_output_path=base_output_path,
                image=img_tensor,
            )
            final_subfolder = (final_subfolder_raw or "").replace("\\", "/")
            _, ext = os.path.splitext(filename_value)

        pil_image = tensor_to_pil(processed_tensor)

        ext_lower = ext.lower()
        format_map = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".webp": "WEBP",
            ".bmp": "BMP",
            ".gif": "GIF",
        }
        save_format = format_map.get(ext_lower, "PNG")
        pil_image.save(output_file, format=save_format)

        payload = {
            "status": "success",
            "data": get_resource_url(final_subfolder, filename_value, save_type),
            "type": save_type,
            "subfolder": final_subfolder,
            "filename": filename_value,
        }
        if extra_payload:
            payload.update(extra_payload)

        return web.json_response(payload, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion


# region Upload
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/upload")
async def lf_nodes_upload(request: web.Request) -> web.Response:
    """Accept a multipart file upload and save to Comfy temp directory.

    Returns a run-style WorkflowAPIResponse wrapped by _make_run_payload.
    The returned path is the absolute file path which can be passed to nodes
    that expect an image path. Files are written with their original filename
    into the temp directory.
    """
    try:
        reader = await request.multipart()
    except Exception as exc:
        logging.warning('Failed to parse multipart upload: %s', exc)
        return web.json_response({
            "message": str(exc),
            "payload": {"detail": str(exc), "error": {"message": 'invalid_multipart'}},
            "status": "error",
        }, status=400)

    paths = []
    temp_dir = folder_paths.get_temp_directory()
    os.makedirs(temp_dir, exist_ok=True)

    try:
        while True:
            part = await reader.next()
            if part is None:
                break

            if part.name in ('directory', 'dir') and not getattr(part, 'filename', None):
                try:
                    dir_value = (await part.text()).strip().lower()
                except Exception:
                    dir_value = ''

                if dir_value:
                    if dir_value not in ('input', 'output', 'temp'):
                        return web.json_response({
                            "message": "invalid_directory",
                            "payload": {"detail": "invalid_directory", "error": {"message": 'invalid_directory_value'}},
                            "status": "error",
                        }, status=400)

                    chosen_dir = folder_paths.get_directory_by_type(dir_value)
                    if not chosen_dir:
                        return web.json_response({
                            "message": "invalid_directory",
                            "payload": {"detail": "invalid_directory", "error": {"message": 'unknown_directory_type'}},
                            "status": "error",
                        }, status=400)

                    temp_dir = chosen_dir
                    os.makedirs(temp_dir, exist_ok=True)

                continue

            if part.name not in ('file', 'files'):
                continue

            raw_filename = part.filename or ""
            sanitized = sanitize_filename(raw_filename)
            if sanitized is None:
                sanitized = f"upload_{int(time.time())}.png"

            dest_path = os.path.join(temp_dir, sanitized)
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = f"{base}_{counter}{ext}"
                counter += 1

            with open(dest_path, 'wb') as f:
                while True:
                    chunk = await part.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)

            paths.append(dest_path)
    except Exception as exc:
        logging.exception('Failed while saving uploaded files: %s', exc)
        return web.json_response({
            "message": str(exc),
            "payload": {"detail": str(exc), "error": {"message": 'save_failed'}},
            "status": "error",
        }, status=500)

    if not paths:
        return web.json_response({
            "message": "missing_file",
            "payload": {"error": {"message": 'missing_file'}},
            "status": "error",
        }, status=400)

    return web.json_response({
        "message": "Upload successful.",
        "payload": {"paths": paths},
        "status": "success",
    }, status=200)
# endregion

# region helpers
def _list_root_directories() -> List[dict]:
    nodes: List[dict] = []

    candidates: List[tuple[str, str]] = []
    if os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            drive_path = f"{letter}:\\"
            if os.path.isdir(drive_path):
                candidates.append((drive_path, f"{letter}:"))
    else:
        root_path = os.path.abspath(os.sep)
        candidates.append((root_path, root_path))

    seen: set[str] = set()

    for path, label in candidates:
        abs_path = os.path.abspath(path)
        if abs_path in seen:
            continue
        seen.add(abs_path)

        image_count, dir_count = _summarize_directory(abs_path)

        metadata = {
            "id": _tree_node_id(abs_path),
            "name": label,
            "paths": {
                "raw": abs_path,
                "relative": "",
                "resolved": abs_path,
            },
            "hasChildren": dir_count > 0,
            "imageCount": image_count,
            "parentId": "root",
            "isRoot": True,
        }

        node = {
            "id": metadata["id"],
            "value": label,
            "cells": {
                "name": {
                    "shape": "text",
                    "value": label,
                },
                "items": {
                    "shape": "text",
                    "value": f"{dir_count} folders • {image_count} images",
                },
                "type": {
                    "shape": "text",
                    "value": "Drive" if os.name == "nt" else "Root",
                },
                "lfCode": {
                    "shape": "code",
                    "value": json.dumps(metadata),
                },
            },
            "children": [],
        }

        nodes.append(node)

    nodes.sort(key=lambda entry: str(entry.get("value", "")).lower())
    return nodes

def _build_root_tree_dataset() -> dict:
    return {
        "columns": TREE_COLUMNS,
        "nodes": _list_root_directories(),
        "parent_id": "root",
    }

def _build_navigation_directory(
    raw_directory: Optional[str],
    images_dir: Optional[str],
    resolved_directory: Optional[str],
    *,
    is_external: bool,
) -> dict:
    navigation_directory: dict[str, object] = {}
    if isinstance(raw_directory, str):
        navigation_directory["raw"] = raw_directory
    if images_dir:
        navigation_directory["resolved"] = images_dir
    if resolved_directory is not None:
        navigation_directory["relative"] = resolved_directory
    navigation_directory["is_external"] = is_external

    return navigation_directory

def _list_image_nodes(
    images_dir: str,
    resolved_directory: Optional[str],
    *,
    is_external: bool,
) -> List[dict]:
    files = []
    try:
        files = sorted(os.listdir(images_dir), key=lambda entry: entry.lower())
    except OSError:
        return []

    nodes: List[dict] = []
    for index, filename in enumerate(files):
        file_path = os.path.join(images_dir, filename)
        if not os.path.isfile(file_path):
            continue
        if not filename.lower().endswith(IMAGE_FILE_EXTENSIONS):
            continue

        if is_external:
            try:
                preview_subfolder, preview_name = ensure_external_preview(images_dir, filename)
            except FileNotFoundError:
                continue
            url = get_resource_url(preview_subfolder, preview_name, "input")
        else:
            url = get_resource_url(resolved_directory or "", filename, "input")

        nodes.append(create_masonry_node(filename, url, index))

    return nodes

def _tree_node_id(path: str) -> str:
    return hashlib.sha1(os.path.abspath(path).encode("utf-8")).hexdigest()

def _summarize_directory(path: str) -> Tuple[int, int]:
    file_count = 0
    dir_count = 0
    try:
        with os.scandir(path) as iterator:
            for entry in iterator:
                if entry.is_dir():
                    dir_count += 1
                elif entry.is_file() and entry.name.lower().endswith(IMAGE_FILE_EXTENSIONS):
                    file_count += 1
    except OSError:
        return 0, 0

    return file_count, dir_count

def _list_directory_children(
    parent_path: str,
    base_path: str,
    *,
    limit: int = MAX_TREE_CHILDREN,
) -> List[dict]:
    try:
        entries = [
            entry
            for entry in os.scandir(parent_path)
            if entry.is_dir()
        ]
    except OSError:
        return []

    entries.sort(key=lambda e: e.name.lower())
    nodes: List[dict] = []

    for entry in entries[:limit]:
        abs_path = entry.path
        rel_path = os.path.relpath(abs_path, base_path)
        if rel_path == ".":
            rel_path = ""

        image_count, dir_count = _summarize_directory(abs_path)

        metadata = {
            "id": _tree_node_id(abs_path),
            "name": entry.name,
            "paths": {
                "relative": rel_path if rel_path != "." else "",
                "resolved": abs_path,
            },
            "hasChildren": dir_count > 0,
            "imageCount": image_count,
            "parentId": _tree_node_id(parent_path),
        }

        node = {
            "id": metadata["id"],
            "value": entry.name,
            "cells": {
                "name": {
                    "shape": "text",
                    "value": entry.name,
                },
                "items": {
                    "shape": "text",
                    "value": f"{image_count} images",
                },
                "type": {
                    "shape": "text",
                    "value": "Folder",
                },
                "lfCode": {
                    "shape": "code",
                    "value": json.dumps(metadata),
                },
            },
            "children": [],
        }

        nodes.append(node)

    return nodes

def _build_tree_dataset(
    base_path: str,
    target_path: str,
    navigation_directory: dict,
    *,
    include_root: bool,
) -> dict:
    base_abs = os.path.abspath(base_path)
    target_abs = os.path.abspath(target_path)

    children = _list_directory_children(target_abs, base_abs)

    dataset = {
        "columns": TREE_COLUMNS,
        "nodes": children,
        "parent_id": _tree_node_id(target_abs),
    }

    if include_root:
        root_metadata = {
            "id": "root",
            "name": navigation_directory.get("raw")
            or navigation_directory.get("relative")
            or "Input",
            "paths": {
                "relative": navigation_directory.get("relative", ""),
                "resolved": target_abs,
            },
            "hasChildren": len(children) > 0,
            "parentId": None,
            "isRoot": True,
        }

        root_node = {
            "id": root_metadata["id"],
            "value": root_metadata["name"],
            "cells": {
                "name": {
                    "shape": "text",
                    "value": root_metadata["name"],
                },
                "items": {
                    "shape": "text",
                    "value": f"{len(children)} folders",
                },
                "type": {
                    "shape": "text",
                    "value": "Root",
                },
                "lfCode": {
                    "shape": "code",
                    "value": json.dumps(root_metadata),
                },
            },
            "children": children,
        }

        dataset = {
            "columns": TREE_COLUMNS,
            "nodes": [root_node],
            "parent_id": "root",
        }

    return dataset

def _build_image_dataset(
    images_dir: str,
    resolved_directory: Optional[str],
    navigation_directory: dict,
    *,
    is_external: bool,
) -> dict:
    dataset: dict = {"nodes": _list_image_nodes(images_dir, resolved_directory, is_external=is_external)}
    dataset["navigation"] = {"directory": navigation_directory}
    return dataset

def _validate_tree_request(
    base_path: str,
    candidate_path: str,
) -> bool:
    base_abs = os.path.abspath(base_path)
    candidate_abs = os.path.abspath(candidate_path)

    try:
        common = os.path.commonpath([base_abs, candidate_abs])
    except ValueError:
        return False

    return common == base_abs

def _load_image_tensor(image_path: str) -> torch.Tensor:
    try:
        pil_image = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    img_tensor = pil_to_tensor(pil_image)

    return img_tensor
# endregion
