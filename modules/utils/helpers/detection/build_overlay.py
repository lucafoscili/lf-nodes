from __future__ import annotations
from typing import Iterable

import cv2
import torch

from ..conversion import tensor_to_numpy

# region build_overlay
def build_overlay(image: torch.Tensor, regions: Iterable[dict]) -> torch.Tensor:
    """
    Draws bounding boxes and labels on an image tensor based on provided region information.

    Args:
        image (torch.Tensor): The input image tensor of shape (C, H, W) or (H, W, C), expected to be in RGB format.
        regions (Iterable[dict]): An iterable of dictionaries, each containing region information with keys:
            - "bbox": List or tuple of four integers [x1, y1, x2, y2] representing the bounding box coordinates.
            - "label": (Optional) String label for the region.
            - "confidence": (Optional) Float or int confidence score for the region.
            - "is_selected": (Optional) Boolean indicating if the region is selected (changes box color).

    Returns:
        torch.Tensor: The image tensor with overlays, normalized to [0, 1], with an added batch dimension.
    """
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
# endregion