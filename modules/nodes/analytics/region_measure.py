"""A region's tone across frames: named pixel boxes, an optional mask, and the Tone profile's numbers per region."""
from __future__ import annotations

import numpy as np
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.tone.boxes import box_mask, check_box, mask_set, parse_boxes, parse_labels
from ...utils.helpers.tone.common import as_rgb
from ...utils.helpers.tone.region_reads import tone_profile
from ...utils.helpers.torch.image_composite import render_label_chip
from ...utils.helpers.ui import create_chart_dataset

SCHEMA = "lf.region-measure.v1"
# Outline colours, one per box in order.
# The widget's charts, one per measure: (the profile's key, the tab's title).
_MEASURES = (("mean", "Luma mean"), ("median", "Luma median"), ("shade", "Shade"), ("fill", "Fill"),
             ("sheen", "Sheen"), ("detail", "Detail"), ("saturation", "Saturation"), ("rb", "Red/blue"),
             ("shade_rb", "Shade red/blue"), ("n", "Pixels"))
_COLOURS = ((1.0, 0.2, 0.2), (0.2, 0.9, 0.2), (0.2, 0.5, 1.0), (1.0, 0.85, 0.1), (1.0, 0.3, 1.0), (0.1, 0.9, 0.9))


def _overlay(rgb: np.ndarray, regions: list[tuple[str, tuple[int, int, int, int] | None]],
             mask: np.ndarray | None) -> torch.Tensor:
    picture = rgb.copy()
    if mask is not None:
        picture[~mask] *= 0.4
    height, width = picture.shape[:2]
    line = max(1, min(height, width) // 200)
    for index, (name, box) in enumerate(regions):
        if box is None:
            continue
        x0, y0, x1, y1 = box
        colour = np.array(_COLOURS[index % len(_COLOURS)], dtype=np.float32)
        picture[y0:min(y0 + line, y1), x0:x1] = colour
        picture[max(y1 - line, y0):y1, x0:x1] = colour
        picture[y0:y1, x0:min(x0 + line, x1)] = colour
        picture[y0:y1, max(x1 - line, x0):x1] = colour
        chip = render_label_chip(name, max_width=max(1, x1 - x0 - 2 * line), max_height=max(1, y1 - y0 - 2 * line),
                                 channels=3)
        if chip is not None:
            chip = chip.numpy()
            top, left = y0 + line, x0 + line
            picture[top:top + chip.shape[0], left:left + chip.shape[1]] = chip
    return torch.from_numpy(picture.astype(np.float32))[None]


def region_measure(image, *, boxes: str = "", labels: str = "", mask=None) -> tuple[dict, list[torch.Tensor]]:
    """Each frame's tone in each named box (narrowed by the mask), in display values 0 to 1."""
    frames = [as_rgb(item, "image") for item in normalize_input_image(image)]
    if not frames:
        raise ValueError("image must hold at least one frame.")
    names = parse_labels(labels, len(frames), "frames")
    regions: list[tuple[str, tuple[int, int, int, int] | None]] = parse_boxes(boxes) or [("frame", None)]
    masks = mask_set(mask, [frame.shape[:2] for frame in frames], "frames")
    report = {"schema": SCHEMA, "unit": "display values 0-1; luma is Rec. 709",
              "regions": [name for name, _ in regions], "frames": []}
    overlays = []
    for index, rgb in enumerate(frames):
        height, width = rgb.shape[:2]
        label = names[index] if names else str(index)
        where = f"frame {index} ({label})" if names else f"frame {index}"
        measured = {}
        for name, box in regions:
            if box is not None:
                try:
                    check_box(name, box, width, height)
                except ValueError as error:
                    raise ValueError(f"{where}: {error}") from None
            region = box_mask(box, height, width)
            if masks is not None:
                region &= masks[index]
            if not region.any():
                raise ValueError(f"{where}: region {name} holds no pixels (its box and the mask do not meet).")
            profile = tone_profile(rgb, region, min_pixels=1)
            profile["box"] = list(box) if box is not None else [0, 0, width, height]
            profile["rgb_mean"] = [float(value) for value in rgb[region].mean(0)]
            profile["rgb_median"] = [float(value) for value in np.median(rgb[region], 0)]
            measured[name] = profile
        report["frames"].append({"frame": index, "label": label, "size": [width, height], "regions": measured})
        overlays.append(_overlay(rgb, regions, masks[index] if masks is not None else None))
    return report, overlays


def measure_datasets(report: dict) -> dict:
    """The widget's charts: a tab per measure, the frames on its axis and a bar series per region."""
    frames = report["frames"]
    labels = [frame["label"] for frame in frames]
    return {title: create_chart_dataset("Frame", labels, [(region, [frame["regions"][region].get(key) for frame in frames])
                                                         for region in report["regions"]], "bar")
            for key, title in _MEASURES}


class LF_RegionMeasure:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Frames to measure, in order; sizes may differ."}),
                "boxes": (Input.STRING, {"default": "", "multiline": True, "tooltip": "Named regions, name=x0,y0,x1,y1 in pixels (end exclusive), one per line or separated by ';'. Empty reads each whole frame."}),
                "labels": (Input.STRING, {"default": "", "tooltip": "Optional frame names, comma separated, one per frame."}),
            },
            "optional": {
                "mask": (Input.MASK, {"tooltip": "Optional mask, one shared or one per frame; it narrows every box."}),
                "ui_widget": (Input.LF_TAB_BAR_CHART, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Measure named boxes across frames: per frame and region its pixel count, luma mean, median, "
                   "deciles, shade, sheen, detail and saturation (Tone profile's numbers), with RGB mean and median.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "lf.region-measure.v1: per frame, each region's numbers in display values 0 to 1.",
        "Frames with their boxes outlined, as a batch (the first stack-compatible size).",
        "Frames with their boxes outlined, one per frame, in order.",
    )
    RETURN_NAMES = ("report", "overlay", "overlay_list")
    RETURN_TYPES = (Input.JSON, Input.IMAGE, Input.IMAGE)

    def on_exec(self, image=None, boxes="", labels="", mask=None, **kwargs):
        report, overlays = region_measure(image, boxes=normalize_list_to_value(boxes) or "",
                                          labels=normalize_list_to_value(labels) or "", mask=mask)
        payload = {"datasets": measure_datasets(report)}
        safe_send_sync("regionmeasure", payload, normalize_list_to_value(kwargs.get("node_id")))
        batch_groups, overlay_list = normalize_output_image(overlays)
        return {"ui": {"lf_output": [payload]}, "result": (report, batch_groups[0], overlay_list)}


NODE_CLASS_MAPPINGS = {"LF_RegionMeasure": LF_RegionMeasure}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_RegionMeasure": "Region measure"}
