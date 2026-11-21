"""Named pixel boxes for the inspection readers: parsing, bounds and the region mask they select."""
from __future__ import annotations

import re

import numpy as np

_NAME = re.compile(r"^[A-Za-z_][\w.-]{0,63}$")


def parse_boxes(text) -> list[tuple[str, tuple[int, int, int, int]]]:
    """``name=x0,y0,x1,y1`` entries (pixels, end exclusive), one per line or separated by ``;``.

    An entry without a name is called ``boxN`` after its place. Empty text gives no boxes.
    """
    boxes: list[tuple[str, tuple[int, int, int, int]]] = []
    for place, raw in enumerate(re.split(r"[;\n]", str(text or "")), start=1):
        entry = raw.strip()
        if not entry:
            continue
        name, _, numbers = entry.rpartition("=")
        name = name.strip() or f"box{len(boxes) + 1}"
        if not _NAME.match(name):
            raise ValueError(f"box name {name!r} must start with a letter and hold letters, digits, '_', '.' or '-'.")
        parts = [part.strip() for part in numbers.split(",")]
        try:
            values = tuple(int(part) for part in parts)
        except ValueError:
            values = ()
        if len(values) != 4:
            raise ValueError(f"box {name} must be x0,y0,x1,y1 in whole pixels, not {numbers.strip()!r}.")
        if any(existing == name for existing, _ in boxes):
            raise ValueError(f"box {name} is named twice.")
        boxes.append((name, values))
    return boxes


def check_box(name: str, box: tuple[int, int, int, int], width: int, height: int) -> None:
    """Refuse an empty box or one reaching outside a width x height image."""
    x0, y0, x1, y1 = box
    if x1 <= x0 or y1 <= y0:
        raise ValueError(f"box {name} {list(box)} is empty: x1 must exceed x0 and y1 exceed y0.")
    if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
        raise ValueError(f"box {name} {list(box)} reaches outside the {width}x{height} image.")


def box_mask(box: tuple[int, int, int, int] | None, height: int, width: int) -> np.ndarray:
    """A boolean [H,W] mask of the box (the whole image without one)."""
    mask = np.zeros((height, width), bool)
    if box is None:
        mask[:] = True
    else:
        x0, y0, x1, y1 = box
        mask[y0:y1, x0:x1] = True
    return mask


def parse_labels(text, count: int, what: str) -> list[str]:
    """Comma or newline separated labels, one per item; empty text gives none."""
    labels = [label.strip() for label in re.split(r"[,\n]", str(text or "")) if label.strip()]
    if labels and len(labels) != count:
        raise ValueError(f"labels name {len(labels)} {what}, not {count}.")
    return labels


def mask_set(masks, sizes: list[tuple[int, int]], what: str) -> list[np.ndarray] | None:
    """One boolean mask per item from a MASK input (one shared, or one per item), each at its item's (H, W)."""
    import torch

    from .common import binary_masks

    if masks is None:
        return None
    if isinstance(masks, (list, tuple)):
        masks = [item for item in masks if item is not None]
        if not masks:
            return None
        masks = torch.cat([item if item.ndim == 3 else item[None] for item in masks], dim=0)
    found = binary_masks(masks)
    if found.ndim == 2:
        found = found[None]
    count = len(sizes)
    if found.shape[0] not in (1, count):
        raise ValueError(f"mask holds {found.shape[0]} masks for {count} {what}: give one, or one per item.")
    chosen = [found[0] if found.shape[0] == 1 else found[index] for index in range(count)]
    for index, (mask, (height, width)) in enumerate(zip(chosen, sizes)):
        if mask.shape != (height, width):
            raise ValueError(f"mask for item {index} is {mask.shape[1]}x{mask.shape[0]}, not its image's "
                             f"{width}x{height}.")
    return chosen
