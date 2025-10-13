import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List, Optional

import folder_paths
from PIL import Image

from ....utils.constants import BASE64_PNG_PREFIX
from .find_checkpoint_image import find_checkpoint_image
from .get_sha256 import get_sha256
from ..conversion import base64_to_tensor, pil_to_tensor, tensor_to_base64

MetadataDict = Dict[str, object]
MetadataCallback = Callable[[MetadataDict], None]

_METADATA_CACHE: Dict[str, MetadataDict] = {}
_INFLIGHT_CALLBACKS: Dict[str, List[MetadataCallback]] = {}
_INFLIGHT_KEYS: set[str] = set()
_METADATA_LOCK = threading.Lock()
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="lf-model-metadata")

# region Helpers
def _metadata_key(model_type: str, model_path: Optional[str]) -> str:
    return f"{model_type}:{model_path or 'None'}"

def _read_saved_info(model_path: Optional[str]) -> Optional[dict]:
    if not model_path:
        return None

    model_info_path = os.path.splitext(model_path)[0] + ".info"
    if not os.path.exists(model_info_path):
        return None

    try:
        with open(model_info_path, "r", encoding="utf-8") as info_file:
            file_content = info_file.read().strip()
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Error reading %s: %s", model_info_path, exc)
        return None

    if not file_content:
        try:
            os.remove(model_info_path)
        except OSError:
            pass
        return None

    try:
        return json.loads(file_content)
    except json.JSONDecodeError as exc:
        logging.getLogger(__name__).warning("JSONDecodeError for %s: %s", model_info_path, exc)
        return None

def _extract_cover_from_saved_info(saved_info: Optional[dict]) -> tuple[Optional[str], Optional[object]]:
    if not saved_info:
        return None, None

    try:
        lf_image_value: str = saved_info["nodes"][0]["cells"]["lfImage"]["value"]
    except (KeyError, IndexError, TypeError):
        logging.getLogger(__name__).debug("lfImage not found in saved_info; skipping inline cover.")
        return None, None

    if not lf_image_value or not lf_image_value.startswith(BASE64_PNG_PREFIX):
        return None, None

    encoded = lf_image_value.replace(BASE64_PNG_PREFIX, "")
    try:
        tensor = base64_to_tensor(encoded)
        return encoded, tensor
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Failed to decode cover image from saved_info: %s", exc)
        return None, None

def _load_cover_from_disk(model_path: Optional[str]) -> tuple[Optional[str], Optional[object]]:
    if not model_path:
        return None, None

    image_path = find_checkpoint_image(model_path)
    if not image_path:
        return None, None

    try:
        with Image.open(image_path) as pil_image:
            tensor = pil_to_tensor(pil_image)
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Failed to open cover image %s: %s", image_path, exc)
        return None, None

    try:
        encoded = tensor_to_base64(tensor)
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Failed to encode cover tensor for %s: %s", image_path, exc)
        return None, None

    return encoded, tensor

def _read_cached_sha256(model_path: Optional[str]) -> Optional[str]:
    if not model_path:
        return None

    hash_path = f"{os.path.splitext(model_path)[0]}.sha256"
    if not os.path.exists(hash_path):
        return None

    try:
        with open(hash_path, "r", encoding="utf-8") as hash_file:
            cached_hash = hash_file.read().strip()
            if cached_hash and len(cached_hash) == 64:
                return cached_hash
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Failed reading cached hash %s: %s", hash_path, exc)

    return None

def _build_basic_metadata(
    model_type: str,
    model_name: Optional[str],
    folder: str,
    *,
    load_cover_from_disk: bool = False,
) -> MetadataDict:
    model_path = folder_paths.get_full_path(folder, model_name)
    saved_info = _read_saved_info(model_path)
    encoded_cover, tensor_cover = _extract_cover_from_saved_info(saved_info)

    if load_cover_from_disk and (encoded_cover is None or tensor_cover is None):
        disk_base64, disk_tensor = _load_cover_from_disk(model_path)
        if disk_base64 is not None and disk_tensor is not None:
            encoded_cover = disk_base64
            tensor_cover = disk_tensor

    return {
        "model_type": model_type,
        "model_name": model_name,
        "model_path": model_path,
        "model_hash": None,
        "model_cover": tensor_cover,
        "model_base64": encoded_cover,
        "saved_info": saved_info,
        "metadata_pending": False,
    }

def _build_quick_metadata(model_type: str, model_name: Optional[str], folder: str) -> MetadataDict:
    metadata = _build_basic_metadata(model_type, model_name, folder, load_cover_from_disk=True)
    model_path = metadata["model_path"]

    if not model_path:
        metadata["metadata_pending"] = False
        return metadata

    cached_hash = _read_cached_sha256(model_path)
    if cached_hash:
        metadata["model_hash"] = cached_hash
        metadata["metadata_pending"] = False
        return metadata

    metadata["metadata_pending"] = True
    return metadata

def _build_full_metadata(model_type: str, model_name: Optional[str], folder: str) -> MetadataDict:
    metadata = _build_basic_metadata(model_type, model_name, folder, load_cover_from_disk=True)
    model_path = metadata["model_path"]

    if not model_path:
        metadata["model_hash"] = None
        metadata["metadata_pending"] = False
        return metadata

    try:
        metadata["model_hash"] = get_sha256(model_path)
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Error calculating hash for %s: %s", model_type, exc)
        metadata["model_hash"] = "Unknown"

    if metadata.get("model_cover") is None or metadata.get("model_base64") is None:
        encoded_cover, tensor_cover = _load_cover_from_disk(model_path)
        metadata["model_cover"] = tensor_cover
        metadata["model_base64"] = encoded_cover

    metadata["metadata_pending"] = False
    return metadata

def _store_metadata_and_notify(key: str, metadata: MetadataDict) -> None:
    callbacks: List[MetadataCallback] = []
    with _METADATA_LOCK:
        _METADATA_CACHE[key] = metadata
        _INFLIGHT_KEYS.discard(key)
        callbacks = _INFLIGHT_CALLBACKS.pop(key, [])

    for callback in callbacks:
        try:
            callback(metadata)
        except Exception as exc:  # noqa: BLE001
            logging.getLogger(__name__).warning("Metadata callback failed: %s", exc)

def _compute_async_metadata(key: str, model_type: str, model_name: Optional[str], folder: str) -> None:
    try:
        metadata = _build_full_metadata(model_type, model_name, folder)
    except Exception:  # noqa: BLE001
        logging.getLogger(__name__).exception("Failed to compute metadata for %s:%s", model_type, model_name)
        metadata = _build_basic_metadata(model_type, model_name, folder)
        metadata["metadata_pending"] = False
        metadata["model_hash"] = "Unknown"

    _store_metadata_and_notify(key, metadata)
# endregion

# region process_model
def process_model(model_type: str, model_name: Optional[str], folder: str) -> MetadataDict:
    """
    Processes a model synchronously by gathering its path, hash, cover, and saved information.

    Args:
        model_type (str): The type of the model.
        model_name (str | None): The name of the model.
        folder (str): The folder where the model is located.

    Returns:
        dict: A dictionary containing the model's path, name, hash, cover, base64 representation, and saved info.
    """
    return _build_full_metadata(model_type, model_name, folder)

def process_model_async(
    model_type: str,
    model_name: Optional[str],
    folder: str,
    *,
    on_complete: Optional[MetadataCallback] = None,
) -> MetadataDict:
    """
    Processes a model without blocking on hash generation. If a cached hash exists it is returned immediately.
    Otherwise the heavy work is scheduled on a background worker and the metadata marked as pending.

    Args:
        model_type: Model type identifier.
        model_name: The selected model name.
        folder: The ComfyUI folder key (e.g. "checkpoints").
        on_complete: Optional callback invoked once full metadata (including hash) is available.

    Returns:
        dict: Metadata describing the model. When the hash is not yet available the dictionary contains
              ``metadata_pending`` set to True and ``model_hash`` is None.
    """
    basic_metadata = _build_quick_metadata(model_type, model_name, folder)
    model_path = basic_metadata.get("model_path")
    key = _metadata_key(model_type, model_path)

    with _METADATA_LOCK:
        cached = _METADATA_CACHE.get(key)
        if cached and not cached.get("metadata_pending", False):
            return cached

        _METADATA_CACHE[key] = basic_metadata

        if not basic_metadata.get("metadata_pending", False):
            return basic_metadata

        callbacks = _INFLIGHT_CALLBACKS.setdefault(key, [])
        if on_complete:
            callbacks.append(on_complete)

        if key not in _INFLIGHT_KEYS:
            _INFLIGHT_KEYS.add(key)
            _EXECUTOR.submit(_compute_async_metadata, key, model_type, model_name, folder)

    return basic_metadata
# endregion
