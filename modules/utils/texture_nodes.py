"""Input pairing and result views shared by the Texture nodes.

The nodes run in list mode: images arrive as flat ``[1, H, W, C]`` items, and
every paired input (masks, references, detail sources) gives either one item
for all images or exactly one per image. Anything else raises.
"""
from __future__ import annotations

import torch

from .helpers.comfy.safe_send_sync import normalize_node_id
from .helpers.logic import normalize_list_to_value, normalize_masks_for_images, normalize_output_image
from .helpers.ui import create_cached_compare_node
from .image_regions import image_items

PREVIEW_LIMIT = 16


def texture_images(value, name: str) -> list[torch.Tensor]:
    """Finite RGB/RGBA images in 0..1 as ``[H, W, C]`` items; at least one."""
    items = image_items(value, name)
    if not items:
        raise ValueError(f"{name} requires at least one image.")
    return [item[0] for item in items]


def paired(items: list, count: int, name: str) -> list:
    """One item broadcast to every image, or exactly one per image."""
    if len(items) == count:
        return items
    if len(items) == 1:
        return items * count
    raise ValueError(f"{name} must hold one item for all {count} image(s) or exactly one per image; "
                     f"got {len(items)}.")


def paired_images(value, count: int, name: str) -> list[torch.Tensor]:
    return paired(texture_images(value, name), count, name)


def absent(value) -> bool:
    """An optional list-mode input that was not connected."""
    return value is None or (isinstance(value, list) and all(item is None for item in value))


def paired_masks(value, count: int, name: str) -> list[torch.Tensor]:
    """Masks as ``[H, W]`` items, one per image (a single mask is broadcast)."""
    if absent(value):
        raise ValueError(f"{name} is required.")
    return paired([mask[0] for mask in normalize_masks_for_images(value, count)], count, name)


def optional_masks(value, count: int, name: str) -> list[torch.Tensor | None]:
    if absent(value):
        return [None] * count
    return paired_masks(value, count, name)


def scalar(value, name: str):
    """A list-mode scalar input: exactly one value."""
    if isinstance(value, list) and len(value) != 1:
        raise ValueError(f"{name} takes one value for the whole node; got {len(value)}.")
    result = normalize_list_to_value(value)
    if result is None:
        raise ValueError(f"{name} is required.")
    return result


def mask_preview(mask: torch.Tensor) -> torch.Tensor:
    """A mask as a grey ``[1, H, W, 3]`` preview image."""
    return mask.detach().to(device="cpu", dtype=torch.float32).clamp(0, 1)[None, ..., None].expand(-1, -1, -1, 3)


def compare_entry(before: torch.Tensor, after: torch.Tensor, index: int, title: str,
                  debug: torch.Tensor | None = None) -> dict:
    return create_cached_compare_node(before[None, ..., :3].cpu(), after[None, ..., :3].cpu(),
                                      index=index, title=title, debug=debug)


def texture_result(results: list[torch.Tensor], receipt: dict, dataset_nodes: list[dict], send, event: str,
                   node_id) -> dict:
    """The node's return value: the first image batch, its receipt and the authoritative list."""
    batches, image_list = normalize_output_image([image[None] for image in results])
    payload = {"dataset": {"nodes": dataset_nodes}, "receipt": receipt}
    send(event, payload, normalize_node_id(node_id))
    return {"ui": {"lf_output": [payload]}, "result": (batches[0], receipt, image_list)}
