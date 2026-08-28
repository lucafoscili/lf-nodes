from __future__ import annotations

from typing import Any, NamedTuple

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch.image_composite import (
    MAX_COMPOSITE_PIXELS,
    resize_composite_image,
)
from ...utils.helpers.ui import cache_generated_preview, create_masonry_node


SPRITE_NORMALIZER_RECEIPT_SCHEMA = "lf.sprite_batch_normalizer.receipt.v1"
_ALPHA_BOUNDS_THRESHOLD = 1.0 / 255.0
_MAX_CANVAS_EDGE = 4096
_MAX_PREVIEWS = 64


class _AlphaBounds(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left + 1

    @property
    def height(self) -> int:
        return self.bottom - self.top + 1

    def to_receipt(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
            "width": self.width,
            "height": self.height,
        }


def _integer(
    value: Any,
    name: str,
    *,
    minimum: int,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer.")
    if value < minimum or (maximum is not None and value > maximum):
        limit = (
            f"between {minimum} and {maximum}"
            if maximum is not None
            else f"greater than or equal to {minimum}"
        )
        raise ValueError(f"{name} must be {limit}.")
    return value


def _round_ratio(numerator: int, denominator: int) -> int:
    """Round a non-negative rational to nearest, with exact halves rounded up."""

    return (2 * numerator + denominator) // (2 * denominator)


def _alpha_bounds(alpha: torch.Tensor, frame_index: int) -> _AlphaBounds:
    support = alpha > _ALPHA_BOUNDS_THRESHOLD
    occupied_rows = torch.nonzero(support.any(dim=1), as_tuple=False).flatten()
    if occupied_rows.numel() == 0:
        raise ValueError(
            f"image frame {frame_index} has empty alpha; every frame must contain "
            "visible sprite content."
        )
    occupied_columns = torch.nonzero(
        support.any(dim=0),
        as_tuple=False,
    ).flatten()
    top = int(occupied_rows[0].item())
    bottom = int(occupied_rows[-1].item())
    left = int(occupied_columns[0].item())
    right = int(occupied_columns[-1].item())
    return _AlphaBounds(left, top, right, bottom)


def _validate_pixel_budget(
    batch_size: int,
    height: int,
    width: int,
    label: str,
) -> None:
    if batch_size * height * width > MAX_COMPOSITE_PIXELS:
        raise ValueError(
            f"{label} exceeds the {MAX_COMPOSITE_PIXELS:,}-pixel safety limit."
        )


def _paste_clipped(
    source: torch.Tensor,
    destination: torch.Tensor,
    *,
    x: int,
    y: int,
) -> None:
    """Place one HWC tensor into a preallocated canvas without wraparound."""

    source_height, source_width, channels = (int(value) for value in source.shape)
    canvas_height, canvas_width, canvas_channels = (
        int(value) for value in destination.shape
    )
    if channels != canvas_channels:
        raise ValueError("source and destination channel counts must match.")

    source_left = max(0, -x)
    source_top = max(0, -y)
    source_right = min(source_width, canvas_width - x)
    source_bottom = min(source_height, canvas_height - y)
    if source_left >= source_right or source_top >= source_bottom:
        return

    destination_left = x + source_left
    destination_top = y + source_top
    destination_right = x + source_right
    destination_bottom = y + source_bottom
    destination[
        destination_top:destination_bottom,
        destination_left:destination_right,
        :,
    ] = source[source_top:source_bottom, source_left:source_right, :]


def normalize_sprite_batch(
    image: Any,
    *,
    canvas_width: int,
    canvas_height: int,
    target_reference_alpha_height: int,
    reference_frame_index: int = 0,
    bottom_padding: int = 0,
) -> tuple[torch.Tensor, dict[str, Any]]:
    """Normalize an RGBA animation batch without per-frame scale or x breathing.

    Alpha bounds are geometric content bounds above 1/255. Equipment, shadows, and
    every other qualifying pixel intentionally count; this function does not infer
    semantic body bounds. Fainter alpha is preserved but ignored for geometry. The
    requested height derives the shared pre-filter scale, while the receipt records
    measured post-filter bounds. Any meaningful alpha clipping fails the whole batch.
    """

    if not isinstance(image, torch.Tensor):
        raise TypeError("image must be a torch.Tensor RGBA IMAGE batch.")
    if image.ndim != 4:
        raise ValueError(
            "image must have rank 4 in [batch, height, width, channels] order."
        )
    batch_size, source_height, source_width, channels = (
        int(value) for value in image.shape
    )
    if batch_size < 1:
        raise ValueError("image batch must contain at least one frame.")
    if source_height < 1 or source_width < 1:
        raise ValueError("image frames must have positive height and width.")
    if channels != 4:
        raise ValueError(
            "image must be RGBA with 4 channels; alpha is required for sprite bounds."
        )
    if not torch.is_floating_point(image):
        raise TypeError("image must be a floating-point IMAGE tensor in [0, 1].")
    if not bool(torch.isfinite(image).all()):
        raise ValueError("image contains NaN or infinite values.")
    _validate_pixel_budget(
        batch_size,
        source_height,
        source_width,
        "image batch",
    )

    canvas_width = _integer(
        canvas_width,
        "canvas_width",
        minimum=1,
        maximum=_MAX_CANVAS_EDGE,
    )
    canvas_height = _integer(
        canvas_height,
        "canvas_height",
        minimum=1,
        maximum=_MAX_CANVAS_EDGE,
    )
    target_reference_alpha_height = _integer(
        target_reference_alpha_height,
        "target_reference_alpha_height",
        minimum=1,
        maximum=canvas_height,
    )
    reference_frame_index = _integer(
        reference_frame_index,
        "reference_frame_index",
        minimum=0,
        maximum=batch_size - 1,
    )
    bottom_padding = _integer(
        bottom_padding,
        "bottom_padding",
        minimum=0,
        maximum=canvas_height - 1,
    )
    if target_reference_alpha_height > canvas_height - bottom_padding:
        raise ValueError(
            "target_reference_alpha_height plus bottom_padding must be less "
            "than or equal to canvas_height."
        )
    _validate_pixel_budget(
        batch_size,
        canvas_height,
        canvas_width,
        "output batch",
    )

    normalized_input = image.to(dtype=torch.float32).clamp(0.0, 1.0)
    source_bounds = [
        _alpha_bounds(normalized_input[index, ..., 3], index)
        for index in range(batch_size)
    ]
    reference_bounds = source_bounds[reference_frame_index]

    resized_height = max(
        1,
        _round_ratio(
            source_height * target_reference_alpha_height,
            reference_bounds.height,
        ),
    )
    resized_width = max(
        1,
        _round_ratio(
            source_width * target_reference_alpha_height,
            reference_bounds.height,
        ),
    )
    _validate_pixel_budget(
        batch_size,
        resized_height,
        resized_width,
        "resized intermediate batch",
    )
    resized = resize_composite_image(
        normalized_input,
        resized_height,
        resized_width,
    )
    scaled_bounds = [
        _alpha_bounds(resized[index, ..., 3], index)
        for index in range(batch_size)
    ]

    scaled_reference = scaled_bounds[reference_frame_index]
    # Work in doubled pixel-center coordinates so the one shared integer
    # translation is deterministic even when either center lies on a half pixel.
    canvas_center_x2 = canvas_width - 1
    reference_center_x2 = scaled_reference.left + scaled_reference.right
    horizontal_translation = _round_ratio(
        abs(canvas_center_x2 - reference_center_x2),
        2,
    )
    if canvas_center_x2 < reference_center_x2:
        horizontal_translation = -horizontal_translation

    target_baseline = canvas_height - bottom_padding - 1
    placements: list[tuple[int, int]] = []
    frame_receipts: list[dict[str, Any]] = []
    for index, bounds in enumerate(scaled_bounds):
        vertical_translation = target_baseline - bounds.bottom
        translated_left = bounds.left + horizontal_translation
        translated_right = bounds.right + horizontal_translation
        translated_top = bounds.top + vertical_translation
        translated_bottom = bounds.bottom + vertical_translation
        clipped_edges = [
            edge
            for edge, clipped in (
                ("left", translated_left < 0),
                ("top", translated_top < 0),
                ("right", translated_right >= canvas_width),
                ("bottom", translated_bottom >= canvas_height),
            )
            if clipped
        ]
        if clipped_edges:
            raise ValueError(
                f"image frame {index} alpha content would be clipped by the "
                f"target canvas at {', '.join(clipped_edges)}; increase the "
                "canvas or reduce target_reference_alpha_height."
            )
        placements.append((horizontal_translation, vertical_translation))
        frame_receipts.append(
            {
                "index": index,
                "sourceAlphaBounds": source_bounds[index].to_receipt(),
                "scaledAlphaBounds": bounds.to_receipt(),
                "translation": {
                    "x": horizontal_translation,
                    "y": vertical_translation,
                },
                "translatedAlphaBounds": {
                    "left": translated_left,
                    "top": translated_top,
                    "right": translated_right,
                    "bottom": translated_bottom,
                },
            }
        )

    output_batch = torch.zeros(
        (batch_size, canvas_height, canvas_width, channels),
        dtype=resized.dtype,
        device=resized.device,
    )
    for index, (x, y) in enumerate(placements):
        _paste_clipped(resized[index], output_batch[index], x=x, y=y)
    receipt = {
        "schema": SPRITE_NORMALIZER_RECEIPT_SCHEMA,
        "batchSize": batch_size,
        "source": {
            "width": source_width,
            "height": source_height,
            "channels": channels,
        },
        "canvas": {
            "width": canvas_width,
            "height": canvas_height,
        },
        "alphaBoundsThreshold": _ALPHA_BOUNDS_THRESHOLD,
        "alphaBoundsComparison": "greater_than",
        "subthresholdAlphaPolicy": "preserved_but_ignored_for_geometry",
        "boundsPolicy": "all_alpha_content_including_props_and_shadows",
        "contentClippingPolicy": "fail",
        "referenceFrameIndex": reference_frame_index,
        "referenceAlphaBounds": reference_bounds.to_receipt(),
        "scaledReferenceAlphaBounds": scaled_reference.to_receipt(),
        "targetReferenceAlphaHeight": target_reference_alpha_height,
        "targetHeightPolicy": "nominal_scale_before_bicubic_rasterization",
        "uniformScale": {
            "numerator": target_reference_alpha_height,
            "denominator": reference_bounds.height,
            "resizedCanvasWidth": resized_width,
            "resizedCanvasHeight": resized_height,
            "filter": "bicubic_antialiased_premultiplied_alpha",
        },
        "horizontalPlacement": {
            "policy": "reference_alpha_bounds_center",
            "translation": horizontal_translation,
        },
        "baseline": {
            "policy": "per_frame_alpha_bottom",
            "bottomPadding": bottom_padding,
            "targetRow": target_baseline,
        },
        "frames": frame_receipts,
    }
    return output_batch, receipt


def _preview_indices(frame_count: int) -> list[int]:
    if frame_count <= _MAX_PREVIEWS:
        return list(range(frame_count))
    return [
        _round_ratio(index * (frame_count - 1), _MAX_PREVIEWS - 1)
        for index in range(_MAX_PREVIEWS)
    ]


class LF_NormalizeSpriteBatch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": (
                            "RGBA sprite animation batch. Every frame needs alpha "
                            "content above 1/255; fainter alpha is preserved but does "
                            "not steer the transform."
                        )
                    },
                ),
                "canvas_width": (
                    Input.INTEGER,
                    {
                        "default": 256,
                        "min": 1,
                        "max": _MAX_CANVAS_EDGE,
                        "step": 1,
                        "tooltip": "Exact transparent output-canvas width in pixels.",
                    },
                ),
                "canvas_height": (
                    Input.INTEGER,
                    {
                        "default": 256,
                        "min": 1,
                        "max": _MAX_CANVAS_EDGE,
                        "step": 1,
                        "tooltip": "Exact transparent output-canvas height in pixels.",
                    },
                ),
                "target_reference_alpha_height": (
                    Input.INTEGER,
                    {
                        "default": 224,
                        "min": 1,
                        "max": _MAX_CANVAS_EDGE,
                        "step": 1,
                        "tooltip": (
                            "Nominal height for the reference frame's alpha bounds. "
                            "It derives one batch-wide scale; bicubic edge filtering "
                            "can add a small measured halo."
                        ),
                    },
                ),
                "reference_frame_index": (
                    Input.INTEGER,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 4095,
                        "step": 1,
                        "tooltip": (
                            "Frame whose alpha height and horizontal center define the "
                            "shared batch transform."
                        ),
                    },
                ),
                "bottom_padding": (
                    Input.INTEGER,
                    {
                        "default": 16,
                        "min": 0,
                        "max": _MAX_CANVAS_EDGE - 1,
                        "step": 1,
                        "tooltip": (
                            "Transparent rows below every frame's alpha baseline. "
                            "Only vertical baseline placement varies per frame."
                        ),
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "RGBA batch on exact canvases, with one shared scale/x pivot and per-frame alpha baseline alignment.",
        "Deterministic lf.sprite_batch_normalizer.receipt.v1 transform receipt.",
        "Individual normalized RGBA frames in batch order.",
    )
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "receipt", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)

    def on_exec(
        self,
        image: torch.Tensor,
        canvas_width: int,
        canvas_height: int,
        target_reference_alpha_height: int,
        reference_frame_index: int = 0,
        bottom_padding: int = 16,
        **kwargs: Any,
    ) -> dict[str, Any]:
        normalized, receipt = normalize_sprite_batch(
            image,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            target_reference_alpha_height=target_reference_alpha_height,
            reference_frame_index=reference_frame_index,
            bottom_padding=bottom_padding,
        )

        displayed_indices = _preview_indices(int(normalized.shape[0]))
        nodes: list[dict[str, Any]] = []
        dataset = {"nodes": nodes}
        for masonry_index, frame_index in enumerate(displayed_indices):
            frame = normalized[frame_index].unsqueeze(0)
            preview = cache_generated_preview(frame)
            node = create_masonry_node(
                f"Normalized frame {frame_index}",
                preview.url,
                masonry_index,
            )
            node["cells"]["lfImage"]["htmlProps"]["title"] = (
                f"Normalized frame {frame_index}"
            )
            nodes.append(node)

        payload = {
            "dataset": dataset,
            "receipt": receipt,
            "preview": {
                "displayedFrameIndices": displayed_indices,
                "displayedFrameCount": len(displayed_indices),
                "totalFrameCount": int(normalized.shape[0]),
                "truncated": len(displayed_indices) < int(normalized.shape[0]),
            },
        }
        safe_send_sync(
            "normalizespritebatch",
            payload,
            normalize_list_to_value(kwargs.get("node_id")),
        )
        _, image_list = normalize_output_image(normalized)
        return {
            "ui": {"lf_output": [payload]},
            "result": (normalized, receipt, image_list),
        }


NODE_CLASS_MAPPINGS = {
    "LF_NormalizeSpriteBatch": LF_NormalizeSpriteBatch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_NormalizeSpriteBatch": "Normalize sprite batch",
}
