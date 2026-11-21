"""Where and by how much two registered images differ: a heat picture per pair and the numbers behind it."""
from __future__ import annotations

import numpy as np
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.tone.boxes import box_mask, check_box, mask_set, parse_boxes, parse_labels
from ...utils.helpers.tone.common import as_rgb, luma
from ...utils.helpers.ui import create_cached_compare_node

SCHEMA = "lf.image-diff.v1"
LEVELS = 255.0
# The heat ramp, from a faint change to the scale's top: violet, magenta, orange, pale yellow.
_RAMP = np.array([(0.25, 0.0, 0.45), (0.75, 0.0, 0.6), (1.0, 0.5, 0.0), (1.0, 1.0, 0.6)], dtype=np.float32)


def _ramp(t: np.ndarray) -> np.ndarray:
    position = np.clip(t, 0, 1) * (len(_RAMP) - 1)
    low = np.floor(position).astype(int).clip(0, len(_RAMP) - 2)
    weight = (position - low)[..., None]
    return _RAMP[low] * (1 - weight) + _RAMP[low + 1] * weight


def _heat(reference: np.ndarray, difference: np.ndarray, region: np.ndarray, scale: float) -> torch.Tensor:
    """The reference in dim grey (dimmer outside the region), coloured where the images differ."""
    base = np.repeat((0.3 * luma(reference))[..., None], 3, axis=-1)
    base[~region] *= 0.5
    t = difference / scale
    weight = np.clip(t * 8, 0, 1)[..., None] * region[..., None]
    picture = base * (1 - weight) + _ramp(t) * weight
    return torch.from_numpy(picture.astype(np.float32))[None]


def image_diff(image_a, image_b, *, threshold: float = 2.0, heat_max: float = 0.0, box: str = "", labels: str = "",
               mask=None) -> tuple[dict, list[torch.Tensor]]:
    """Compare each pair (exact pairs, or one A against every B) over an optional box and mask.

    Differences are in 8-bit levels of the stored display values, per pixel the largest of the three channels.
    """
    images_a, images_b = normalize_input_image(image_a), normalize_input_image(image_b)
    if not images_a or not images_b:
        raise ValueError("image_a and image_b must each hold an image.")
    if len(images_a) != len(images_b) and len(images_a) != 1:
        raise ValueError(f"{len(images_a)} images in image_a and {len(images_b)} in image_b: give one A per B, "
                         "or one A for every B.")
    count = len(images_b)
    names = parse_labels(labels, count, "pairs")
    boxes = parse_boxes(box)
    if len(boxes) > 1:
        raise ValueError(f"box holds {len(boxes)} boxes; Image diff reads one region.")
    pairs = []
    for index in range(count):
        a = as_rgb(images_a[0] if len(images_a) == 1 else images_a[index], "image_a")
        b = as_rgb(images_b[index], "image_b")
        if a.shape != b.shape:
            raise ValueError(f"pair {index}: image_a is {a.shape[1]}x{a.shape[0]} and image_b is "
                             f"{b.shape[1]}x{b.shape[0]}; a diff needs registered images of one size.")
        pairs.append((a, b))
    masks = mask_set(mask, [a.shape[:2] for a, _ in pairs], "pairs")
    found = []
    for index, (a, b) in enumerate(pairs):
        height, width = a.shape[:2]
        region_box = boxes[0][1] if boxes else None
        if region_box is not None:
            check_box(boxes[0][0], region_box, width, height)
        region = box_mask(region_box, height, width)
        if masks is not None:
            region &= masks[index]
        if not region.any():
            raise ValueError(f"pair {index}: the region holds no pixels (box and mask do not meet).")
        difference = np.abs(b - a).max(-1) * LEVELS
        found.append((a, b, difference, region, region_box))
    scale = float(heat_max) if heat_max > 0 else max(max(float(item[2][item[3]].max()) for item in found), 1.0)
    report = {"schema": SCHEMA, "unit": "8-bit levels, largest channel", "threshold": float(threshold),
              "scale_levels": scale, "pairs": []}
    heats = []
    for index, (a, b, difference, region, region_box) in enumerate(found):
        inside = difference[region]
        changed = region & (difference > threshold)
        rows, columns = np.nonzero(changed)
        changed_box = None
        if rows.size:
            changed_box = [int(columns.min()), int(rows.min()), int(columns.max()) + 1, int(rows.max()) + 1]
        luma_a, luma_b = float(luma(a)[region].mean() * LEVELS), float(luma(b)[region].mean() * LEVELS)
        report["pairs"].append({
            "pair": index,
            "label": names[index] if names else str(index),
            "size": [int(a.shape[1]), int(a.shape[0])],
            "box": list(region_box) if region_box is not None else None,
            "pixels": int(region.sum()),
            "mean": float(inside.mean()),
            "median": float(np.median(inside)),
            "p95": float(np.quantile(inside, 0.95)),
            "p99": float(np.quantile(inside, 0.99)),
            "max": float(inside.max()),
            "changed_pixels": int(changed.sum()),
            "changed_share": float(changed.sum() / region.sum()),
            "changed_box": changed_box,
            "luma_a": luma_a,
            "luma_b": luma_b,
            "luma_delta": luma_b - luma_a,
        })
        heats.append(_heat(a, difference, region, scale))
    return report, heats


class LF_ImageDiff:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": (Input.IMAGE, {"tooltip": "Reference images: one per B, or one for every B."}),
                "image_b": (Input.IMAGE, {"tooltip": "Compared images, each registered with its A and of its size."}),
                "threshold": (Input.FLOAT, {"default": 2.0, "min": 0.0, "max": 255.0, "step": 0.5, "tooltip": "A pixel counts as changed above this many 8-bit levels."}),
                "heat_max": (Input.FLOAT, {"default": 0.0, "min": 0.0, "max": 255.0, "step": 0.5, "tooltip": "Levels at the top of the heat ramp; 0 uses the largest difference over all pairs, so every pair shares one scale."}),
                "box": (Input.STRING, {"default": "", "tooltip": "Optional region, x0,y0,x1,y1 in pixels (end exclusive); empty reads the whole image."}),
                "labels": (Input.STRING, {"default": "", "tooltip": "Optional pair names, comma separated, one per pair."}),
            },
            "optional": {
                "mask": (Input.MASK, {"tooltip": "Optional region mask, one shared or one per pair; it narrows the box."}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Compare registered images pair by pair: a heat picture of where they differ over the reference "
                   "in grey, and the numbers (mean, median, p95, p99, max, changed share and box, luma shift).")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Heat pictures as a batch (the first stack-compatible size).",
        "Heat pictures, one per pair, in order.",
        "lf.image-diff.v1: per pair, the region's difference in 8-bit levels and its changed share and box.",
    )
    RETURN_NAMES = ("heat", "heat_list", "report")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON)

    def on_exec(self, image_a=None, image_b=None, threshold=2.0, heat_max=0.0, box="", labels="", mask=None,
                **kwargs):
        report, heats = image_diff(
            image_a, image_b, threshold=float(normalize_list_to_value(threshold)),
            heat_max=float(normalize_list_to_value(heat_max)), box=normalize_list_to_value(box) or "",
            labels=normalize_list_to_value(labels) or "", mask=mask)
        images_b = normalize_input_image(image_b)
        nodes = []
        for index, (heat, pair) in enumerate(zip(heats, report["pairs"])):
            title = f"{pair['label']}: max {pair['max']:.1f}, changed {pair['changed_share'] * 100:.2f}%"
            nodes.append(create_cached_compare_node(images_b[index], heat, index=index, title=title))
        payload = {"dataset": {"nodes": nodes}, "report": report}
        safe_send_sync("imagediff", payload, normalize_list_to_value(kwargs.get("node_id")))
        batch_groups, heat_list = normalize_output_image(heats)
        return {"ui": {"lf_output": [payload]}, "result": (batch_groups[0], heat_list, report)}


NODE_CLASS_MAPPINGS = {"LF_ImageDiff": LF_ImageDiff}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_ImageDiff": "Image diff"}
