from __future__ import annotations

import math
from typing import Any

import torch
from torch.nn import functional

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import cache_generated_preview, create_masonry_node
from .periodic_image_batch_sampler import periodic_sample_indices


LOOP_SEGMENT_RECEIPT_SCHEMA = "lf.select_loop_segment.receipt.v1"
_MAX_PREVIEWS = 64
_TOP_CANDIDATES = 5
_DEFAULT_ANALYSIS_MAX_EDGE = 96


def _positive_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive finite number.")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a positive finite number.") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{name} must be a positive finite number.")
    return parsed


def _integer(value: Any, name: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer of at least {minimum}.")
    if value < minimum:
        raise ValueError(f"{name} must be an integer of at least {minimum}.")
    return value


def analysis_frames(image: torch.Tensor, max_edge: int) -> torch.Tensor:
    """Grey, area-downsampled copies scaled to 0..255 for cheap motion scoring."""

    if not isinstance(image, torch.Tensor) or image.ndim != 4:
        raise ValueError("image must be a batch shaped [frames, height, width, channels].")
    frames = image[..., :3].float().mean(dim=3)
    _count, height, width = frames.shape
    scale = min(1.0, float(max_edge) / float(max(height, width)))
    if scale < 1.0:
        size = (max(1, round(height * scale)), max(1, round(width * scale)))
        frames = functional.interpolate(frames.unsqueeze(1), size=size, mode="area").squeeze(1)
    return frames * 255.0


def score_loop_candidates(
    gray: torch.Tensor,
    *,
    min_period: int,
    max_period: int,
    motion_floor: float,
) -> dict[str, Any]:
    """Score every (start, period) by seam / in-segment motion.

    The frame that would follow the last looped frame must look like the first
    (small seam), and the segment must actually move (mean inter-frame step at
    least ``motion_floor`` times the whole shot's median), so a frozen stretch
    can never win on a trivially small seam.
    """

    count = int(gray.shape[0])
    if count < 3:
        raise ValueError("At least three frames are needed to find a loop.")
    step = (gray[1:] - gray[:-1]).abs().mean(dim=(1, 2))
    median_step = float(step.median())
    cumulative = torch.cat([torch.zeros(1, dtype=step.dtype), step.cumsum(0)])
    effective_max = min(max_period, count - 1)
    candidates: list[dict[str, float | int]] = []
    for period in range(min_period, effective_max + 1):
        starts = count - period
        seam = (gray[:starts] - gray[period : period + starts]).abs().mean(dim=(1, 2))
        motion = (cumulative[period : period + starts] - cumulative[:starts]) / float(period)
        keep = motion >= motion_floor * median_step
        if median_step <= 0.0 and motion_floor > 0.0:
            keep = torch.zeros_like(keep)
        for start in torch.nonzero(keep, as_tuple=False).flatten().tolist():
            seam_value = float(seam[start])
            motion_value = float(motion[start])
            candidates.append(
                {
                    "start": int(start),
                    "period": int(period),
                    "seam": seam_value,
                    "motion": motion_value,
                    "ratio": seam_value / max(motion_value, 1e-6),
                }
            )
    # Ties (an exactly periodic shot scores every multiple the same) keep the shortest cycle.
    candidates.sort(key=lambda item: (item["ratio"], item["period"], item["start"]))
    return {
        "median_step": median_step,
        "effective_max_period": effective_max,
        "candidates": candidates,
    }


def select_loop_segment(
    image: torch.Tensor,
    *,
    source_fps: float,
    target_count: int,
    min_period_frames: int,
    max_period_frames: int,
    motion_floor: float = 0.6,
    analysis_max_edge: int = _DEFAULT_ANALYSIS_MAX_EDGE,
) -> tuple[torch.Tensor, dict[str, Any]]:
    source_fps = _positive_float(source_fps, "source_fps")
    target_count = _integer(target_count, "target_count", minimum=1)
    min_period_frames = _integer(min_period_frames, "min_period_frames", minimum=2)
    max_period_frames = _integer(max_period_frames, "max_period_frames", minimum=min_period_frames)
    analysis_max_edge = _integer(analysis_max_edge, "analysis_max_edge", minimum=8)
    if isinstance(motion_floor, bool) or not isinstance(motion_floor, (int, float)):
        raise ValueError("motion_floor must be a number between 0 and 4.")
    motion_floor = float(motion_floor)
    if not math.isfinite(motion_floor) or motion_floor < 0.0 or motion_floor > 4.0:
        raise ValueError("motion_floor must be a number between 0 and 4.")

    gray = analysis_frames(image, analysis_max_edge)
    scored = score_loop_candidates(
        gray,
        min_period=min_period_frames,
        max_period=max_period_frames,
        motion_floor=motion_floor,
    )
    usable = [item for item in scored["candidates"] if item["period"] >= target_count]
    if not usable:
        raise ValueError(
            "No loop segment satisfies the constraints: need a period between "
            f"{min_period_frames} and {scored['effective_max_period']} frames, at least "
            f"{target_count} frames long, moving at least {motion_floor:.2f} x the median "
            "inter-frame step. Lower motion_floor, widen the period range, or shorten the target."
        )
    best = usable[0]
    start = int(best["start"])
    period = int(best["period"])
    offsets = periodic_sample_indices(period + 1, target_count, "exclude_final_endpoint")
    indices = [start + offset for offset in offsets]
    sampled = image[indices].contiguous()
    cycle_seconds = float(period) / source_fps
    receipt = {
        "schema": LOOP_SEGMENT_RECEIPT_SCHEMA,
        "sourceFrameCount": int(image.shape[0]),
        "sourceFps": source_fps,
        "analysisMaxEdge": analysis_max_edge,
        "medianStep": scored["median_step"],
        "motionFloor": motion_floor,
        "minPeriodFrames": min_period_frames,
        "maxPeriodFrames": scored["effective_max_period"],
        "candidateCount": len(usable),
        "selected": {
            "start": start,
            "periodFrames": period,
            "seam": float(best["seam"]),
            "motion": float(best["motion"]),
            "ratio": float(best["ratio"]),
            "cycleSeconds": cycle_seconds,
        },
        "topCandidates": [
            {
                "start": int(item["start"]),
                "periodFrames": int(item["period"]),
                "seam": float(item["seam"]),
                "motion": float(item["motion"]),
                "ratio": float(item["ratio"]),
            }
            for item in usable[:_TOP_CANDIDATES]
        ],
        "targetCount": target_count,
        "intendedFps": float(target_count) / cycle_seconds,
        "sampledSourceIndices": indices,
    }
    return sampled, receipt


def _preview_indices(count: int) -> list[int]:
    if count <= _MAX_PREVIEWS:
        return list(range(count))
    return [round(index * (count - 1) / (_MAX_PREVIEWS - 1)) for index in range(_MAX_PREVIEWS)]


class LF_SelectLoopSegment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": (
                            "Ordered frames of one shot (for example a decoded video). The "
                            "best self-closing segment is chosen and resampled to target_count "
                            "frames, excluding the final endpoint so the loop closes."
                        )
                    },
                ),
                "source_fps": (
                    Input.FLOAT,
                    {
                        "default": 24.0,
                        "min": 0.01,
                        "max": 1000.0,
                        "step": 0.01,
                        "tooltip": "Frame rate of the source frames; derives cycle seconds.",
                    },
                ),
                "target_count": (
                    Input.INTEGER,
                    {
                        "default": 24,
                        "min": 1,
                        "max": 4096,
                        "step": 1,
                        "tooltip": "Frames in the output loop. Periods shorter than this are ignored.",
                    },
                ),
                "min_period_frames": (
                    Input.INTEGER,
                    {
                        "default": 12,
                        "min": 2,
                        "max": 4096,
                        "step": 1,
                        "tooltip": "Shortest cycle to consider, in source frames.",
                    },
                ),
                "max_period_frames": (
                    Input.INTEGER,
                    {
                        "default": 96,
                        "min": 2,
                        "max": 4096,
                        "step": 1,
                        "tooltip": "Longest cycle to consider, in source frames (clamped to the shot).",
                    },
                ),
                "motion_floor": (
                    Input.FLOAT,
                    {
                        "default": 0.6,
                        "min": 0.0,
                        "max": 4.0,
                        "step": 0.05,
                        "tooltip": (
                            "Minimum mean inter-frame motion inside a candidate, as a "
                            "multiple of the shot's median step. Keeps frozen stretches from winning."
                        ),
                    },
                ),
            },
            "optional": {
                "analysis_max_edge": (
                    Input.INTEGER,
                    {
                        "default": _DEFAULT_ANALYSIS_MAX_EDGE,
                        "min": 8,
                        "max": 1024,
                        "step": 1,
                        "tooltip": "Longest edge of the grey analysis copies.",
                    },
                ),
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = (
        "Pick the best self-closing loop out of a shot by seam versus motion, then "
        "resample it to a fixed frame count for a sprite atlas."
    )
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "receipt", "image_list")
    OUTPUT_TOOLTIPS = (
        "Sampled loop frames as one batch, in playback order; pixels are unchanged.",
        "Loop-selection receipt: chosen start/period, seam and motion scores, sampled indices.",
        "The same sampled frames as an authoritative list.",
    )
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)

    def on_exec(
        self,
        image: torch.Tensor,
        source_fps: float,
        target_count: int,
        min_period_frames: int,
        max_period_frames: int,
        motion_floor: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        analysis_max_edge = (
            normalize_list_to_value(kwargs["analysis_max_edge"])
            if "analysis_max_edge" in kwargs
            else _DEFAULT_ANALYSIS_MAX_EDGE
        )
        sampled, receipt = select_loop_segment(
            image,
            source_fps=normalize_list_to_value(source_fps),
            target_count=normalize_list_to_value(target_count),
            min_period_frames=normalize_list_to_value(min_period_frames),
            max_period_frames=normalize_list_to_value(max_period_frames),
            motion_floor=normalize_list_to_value(motion_floor),
            analysis_max_edge=analysis_max_edge,
        )

        displayed_indices = _preview_indices(int(sampled.shape[0]))
        nodes: list[dict[str, Any]] = []
        dataset = {"nodes": nodes}
        for masonry_index, output_frame_index in enumerate(displayed_indices):
            frame = sampled[output_frame_index].unsqueeze(0)
            preview = cache_generated_preview(frame)
            node = create_masonry_node(
                f"Loop frame {output_frame_index}",
                preview.url,
                masonry_index,
            )
            node["cells"]["lfImage"]["htmlProps"]["title"] = f"Loop frame {output_frame_index}"
            nodes.append(node)

        payload = {
            "dataset": dataset,
            "receipt": receipt,
            "preview": {
                "displayedOutputFrameIndices": displayed_indices,
                "displayedFrameCount": len(displayed_indices),
                "totalOutputFrameCount": int(sampled.shape[0]),
                "truncated": len(displayed_indices) < int(sampled.shape[0]),
            },
        }
        safe_send_sync(
            "selectloopsegment",
            payload,
            normalize_list_to_value(kwargs.get("node_id")),
        )
        _, image_list = normalize_output_image(sampled)
        return {
            "ui": {"lf_output": [payload]},
            "result": (sampled, receipt, image_list),
        }


NODE_CLASS_MAPPINGS = {
    "LF_SelectLoopSegment": LF_SelectLoopSegment,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SelectLoopSegment": "Select loop segment",
}
