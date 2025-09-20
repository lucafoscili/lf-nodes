from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional

import cv2
import torch

import folder_paths

from .helpers import (
    create_compare_node,
    get_resource_url,
    resolve_filepath,
    tensor_to_numpy,
    tensor_to_pil,
)

ONNX_ROOT = Path(folder_paths.models_dir) / "onnx"

def discover_ultralytics_models() -> Dict[str, Path]:
    """Return mapping of display labels to ONNX model paths under models/onnx."""
    discovered: Dict[str, Path] = {}
    try:
        root_exists = ONNX_ROOT.exists()
    except OSError:
        root_exists = False
    if not root_exists:
        return discovered
    for file in sorted(ONNX_ROOT.rglob("*.onnx")):
        try:
            relative = file.relative_to(ONNX_ROOT)
        except ValueError:
            label = file.name
        else:
            label = str(relative).replace("\\", "/")
        discovered[label] = file
    return discovered


def parse_class_filter(raw_value: str) -> Optional[List[str]]:
    tokens = [segment.strip() for segment in str(raw_value).replace(";", ",").split(",") if segment.strip()]
    return tokens or None


def select_region(
    regions: List[dict],
    select_index: int,
    strategy: str,
    preferred_label: Optional[str],
) -> Optional[dict]:
    if not regions:
        return None

    if preferred_label:
        for region in regions:
            label = (region.get("label") or "").lower()
            if label == preferred_label:
                region["selection_reason"] = "preferred_label"
                return region

    if select_index >= 0:
        if select_index < len(regions):
            region = regions[select_index]
            region["selection_reason"] = "index"
            region["selection_index"] = select_index
            return region

    metric = "area" if strategy == "area" else "confidence"
    region = max(regions, key=lambda item: float(item.get(metric, 0.0)))
    region["selection_reason"] = metric
    return region


def build_overlay(image: torch.Tensor, regions: Iterable[dict]) -> torch.Tensor:
    base_rgb = tensor_to_numpy(image, threeD=True)
    overlay = cv2.cvtColor(base_rgb, cv2.COLOR_RGB2BGR)
    height, width = overlay.shape[:2]
    scale = max(height, width) / 640.0
    font_scale = max(0.4, 0.5 * scale)
    thickness = max(1, int(round(1.5 * scale)))

    for region in regions:
        bbox = region.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1 = max(0, min(x1, width - 1))
        x2 = max(0, min(x2, width - 1))
        y1 = max(0, min(y1, height - 1))
        y2 = max(0, min(y2, height - 1))
        color = (0, 255, 0)
        if region.get("is_selected"):
            color = (0, 165, 255)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thickness)

        label = region.get("label") or "region"
        confidence = region.get("confidence")
        text = f"{label} {confidence:.2f}" if isinstance(confidence, (int, float)) else label
        text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_x1 = x1
        text_y1 = max(0, y1 - text_size[1] - baseline - 2)
        text_x2 = min(width, text_x1 + text_size[0] + 6)
        text_y2 = max(0, y1)
        cv2.rectangle(overlay, (text_x1, text_y1), (text_x2, text_y2), color, -1)
        text_origin = (text_x1 + 3, text_y2 - baseline - 1)
        cv2.putText(
            overlay,
            text,
            text_origin,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 0, 0),
            max(1, thickness - 1),
            lineType=cv2.LINE_AA,
        )

    overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
    overlay_tensor = torch.from_numpy(overlay.astype("float32") / 255.0)
    return overlay_tensor.unsqueeze(0)


def append_compare_entry(
    original: torch.Tensor,
    overlay: torch.Tensor,
    nodes: List[dict],
    index: int,
) -> None:
    orig_path, orig_sub, orig_name = resolve_filepath("detect_regions_orig", image=original)
    tensor_to_pil(original).save(orig_path, "PNG")

    overlay_path, overlay_sub, overlay_name = resolve_filepath("detect_regions_overlay", image=overlay)
    tensor_to_pil(overlay).save(overlay_path, "PNG")

    url_before = get_resource_url(orig_sub, orig_name, "temp")
    url_after = get_resource_url(overlay_sub, overlay_name, "temp")
    nodes.append(create_compare_node(url_before, url_after, index))
