from __future__ import annotations

import math
from typing import Any

import torch
from torch.nn import functional

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import (
    normalize_input_image_batches,
    normalize_list_to_value,
)
from ...utils.helpers.ui import cache_generated_preview, create_masonry_node


SETTLED_FRAME_RECEIPT_SCHEMA = "lf.select_settled_image_frame.receipt.v1"
_ANALYSIS_CHUNK_SIZE = 8
_MIN_ANALYSIS_MAX_EDGE = 8
_MAX_ANALYSIS_MAX_EDGE = 1024


def _tail_fraction(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("tail_fraction must be a finite number greater than 0 and at most 1.")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            "tail_fraction must be a finite number greater than 0 and at most 1."
        ) from error
    if not math.isfinite(parsed) or parsed <= 0 or parsed > 1:
        raise ValueError(
            "tail_fraction must be a finite number greater than 0 and at most 1."
        )
    return parsed


def _analysis_max_edge(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("analysis_max_edge must be an integer between 8 and 1024.")
    if value < _MIN_ANALYSIS_MAX_EDGE or value > _MAX_ANALYSIS_MAX_EDGE:
        raise ValueError("analysis_max_edge must be an integer between 8 and 1024.")
    return value


def _coherent_image_batch(image: Any) -> torch.Tensor:
    batches = normalize_input_image_batches(image)
    if not batches:
        raise ValueError("image must contain at least one RGB or RGBA frame.")

    first = batches[0]
    expected_shape = tuple(first.shape[1:])
    expected_dtype = first.dtype
    expected_device = first.device
    for batch in batches[1:]:
        if (
            tuple(batch.shape[1:]) != expected_shape
            or batch.dtype != expected_dtype
            or batch.device != expected_device
        ):
            raise ValueError(
                "image must be one coherent sequence: every frame must share height, "
                "width, RGB/RGBA channels, dtype, and device."
            )

    return first if len(batches) == 1 else torch.cat(batches, dim=0)


def _visual_analysis_frames(
    image: torch.Tensor,
    *,
    max_edge: int,
) -> tuple[torch.Tensor, int, int]:
    """Build bounded CPU frames for deterministic local-motion scoring."""

    _, height, width, channels = image.shape
    scale = min(1.0, max_edge / max(int(height), int(width)))
    analysis_height = max(1, round(int(height) * scale))
    analysis_width = max(1, round(int(width) * scale))
    chunks: list[torch.Tensor] = []

    for start in range(0, int(image.shape[0]), _ANALYSIS_CHUNK_SIZE):
        chunk = image[start : start + _ANALYSIS_CHUNK_SIZE].detach().permute(
            0, 3, 1, 2
        )
        if not bool(torch.isfinite(chunk).all()):
            raise ValueError("image tail contains NaN or infinite pixel values.")
        chunk = chunk.to(dtype=torch.float32)
        if (analysis_height, analysis_width) != (int(height), int(width)):
            chunk = functional.interpolate(
                chunk,
                size=(analysis_height, analysis_width),
                mode="bilinear",
                align_corners=False,
                antialias=True,
            )

        rgb = chunk[:, :3].clamp(0.0, 1.0)
        if channels == 4:
            alpha = chunk[:, 3:4].clamp(0.0, 1.0)
            chunk = torch.cat((rgb * alpha, alpha), dim=1)
        else:
            chunk = rgb
        chunks.append(chunk.cpu())

    return torch.cat(chunks, dim=0), analysis_height, analysis_width


def select_settled_image_frame(
    image: Any,
    *,
    tail_fraction: Any,
    analysis_max_edge: Any,
) -> tuple[torch.Tensor, int, dict[str, Any]]:
    """Select the locally least-changing frame in the final input window.

    The score is the mean absolute visual difference to each available adjacent
    frame. Exact score ties resolve to the latest frame. This is deliberately a
    pixel-motion metric: it does not understand pose, angle, anatomy, or identity.
    """

    resolved_tail_fraction = _tail_fraction(tail_fraction)
    resolved_analysis_max_edge = _analysis_max_edge(analysis_max_edge)
    batch = _coherent_image_batch(image)
    source_frame_count, source_height, source_width, channels = (
        int(value) for value in batch.shape
    )

    tail_frame_count = max(
        1,
        math.ceil(source_frame_count * resolved_tail_fraction),
    )
    candidate_start = source_frame_count - tail_frame_count
    analysis_start = max(0, candidate_start - 1)
    analysis, analysis_height, analysis_width = _visual_analysis_frames(
        batch[analysis_start:],
        max_edge=resolved_analysis_max_edge,
    )
    transition_scores = analysis[1:].sub(analysis[:-1]).abs().mean(dim=(1, 2, 3))

    raw_candidate_scores: list[tuple[int, float]] = []
    for source_index in range(candidate_start, source_frame_count):
        local_index = source_index - analysis_start
        adjacent_scores: list[torch.Tensor] = []
        if local_index > 0:
            adjacent_scores.append(transition_scores[local_index - 1])
        if local_index < int(analysis.shape[0]) - 1:
            adjacent_scores.append(transition_scores[local_index])
        score = (
            float(torch.stack(adjacent_scores).mean())
            if adjacent_scores
            else 0.0
        )
        raw_candidate_scores.append((source_index, score))

    selected_index, selected_score = min(
        raw_candidate_scores,
        key=lambda candidate: (candidate[1], -candidate[0]),
    )
    selected = batch[selected_index : selected_index + 1]
    receipt = {
        "schema": SETTLED_FRAME_RECEIPT_SCHEMA,
        "source": {
            "frameCount": source_frame_count,
            "width": source_width,
            "height": source_height,
            "channels": channels,
        },
        "tailFraction": resolved_tail_fraction,
        "tailFrameCount": tail_frame_count,
        "candidateRange": {
            "startIndex": candidate_start,
            "endIndex": source_frame_count - 1,
        },
        "selectedIndex": selected_index,
        "selectedScore": round(selected_score, 12),
        "analysis": {
            "requestedMaxEdge": resolved_analysis_max_edge,
            "width": analysis_width,
            "height": analysis_height,
            "frameRange": {
                "startIndex": analysis_start,
                "endIndex": source_frame_count - 1,
            },
            "metric": "mean_absolute_rgb_or_premultiplied_rgba",
            "frameScorePolicy": "mean_available_adjacent_transition_scores",
            "tieBreak": "latest_frame",
            "resize": "torch_bilinear_antialiased",
            "scoringBackend": "cpu",
        },
        "candidates": [
            {"index": index, "score": round(score, 12)}
            for index, score in raw_candidate_scores
        ],
        "semanticValidation": "none",
    }
    return selected, selected_index, receipt


class LF_SelectSettledImageFrame:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": (
                            "Ordered coherent RGB or RGBA frames. The selector "
                            "measures image change only; it does not recognize the "
                            "correct angle, pose, anatomy, or identity."
                        )
                    },
                ),
                "tail_fraction": (
                    Input.FLOAT,
                    {
                        "default": 0.25,
                        "min": 0.01,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": (
                            "Final fraction of the sequence eligible for selection. "
                            "For example, 0.25 searches only the last quarter."
                        ),
                    },
                ),
                "analysis_max_edge": (
                    Input.INTEGER,
                    {
                        "default": 96,
                        "min": _MIN_ANALYSIS_MAX_EDGE,
                        "max": _MAX_ANALYSIS_MAX_EDGE,
                        "step": 8,
                        "tooltip": (
                            "Longest edge used only for motion analysis. Higher values "
                            "notice smaller pixel changes but require more work; the "
                            "selected output keeps its original pixels."
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
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True, False, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Exact selected source frame as a one-image batch; RGB/RGBA pixels are unchanged.",
        "Authoritative one-item list containing the exact selected source frame.",
        "Zero-based selected source-frame index.",
        "Deterministic motion scores and selection policy; no semantic validation is performed.",
    )
    RETURN_NAMES = ("image", "image_list", "selected_index", "receipt")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.INTEGER, Input.JSON)

    def on_exec(
        self,
        image: Any,
        tail_fraction: Any,
        analysis_max_edge: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        selected, selected_index, receipt = select_settled_image_frame(
            image,
            tail_fraction=normalize_list_to_value(tail_fraction),
            analysis_max_edge=normalize_list_to_value(analysis_max_edge),
        )

        preview = cache_generated_preview(selected)
        label = f"Selected frame {selected_index}"
        dataset = {
            "nodes": [create_masonry_node(label, preview.url, 0)],
        }
        payload = {"dataset": dataset, "receipt": receipt}
        safe_send_sync(
            "selectsettledimageframe",
            payload,
            normalize_list_to_value(kwargs.get("node_id")),
        )
        return {
            "ui": {"lf_output": [payload]},
            "result": (selected, [selected], selected_index, receipt),
        }


NODE_CLASS_MAPPINGS = {
    "LF_SelectSettledImageFrame": LF_SelectSettledImageFrame,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SelectSettledImageFrame": "Select settled image frame",
}
