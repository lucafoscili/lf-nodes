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


PERIODIC_SAMPLER_RECEIPT_SCHEMA = "lf.periodic_image_batch_sampler.receipt.v1"
LOOP_ENDPOINT_POLICIES = ["exclude_final_endpoint", "include_final_endpoint"]
SAMPLING_BASES = ["timeline", "visual_motion"]
_MAX_PREVIEWS = 64
_ANALYSIS_MAX_EDGE = 96
_ANALYSIS_CHUNK_SIZE = 8


def _positive_fps(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive finite number.")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a positive finite number.") from error
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{name} must be a positive finite number.")
    return parsed


def _nearest_index(numerator: int, denominator: int) -> int:
    """Round a non-negative rational to nearest, with exact halves rounded up."""

    return (2 * numerator + denominator) // (2 * denominator)


def periodic_sample_indices(
    source_count: int,
    target_count: int,
    loop_endpoint_policy: str,
) -> list[int]:
    if type(source_count) is not int or source_count < 1:
        raise ValueError("source_count must be a positive integer.")
    if type(target_count) is not int or target_count < 1:
        raise ValueError("target_count must be a positive integer.")
    if loop_endpoint_policy not in LOOP_ENDPOINT_POLICIES:
        raise ValueError(
            "loop_endpoint_policy must be exclude_final_endpoint or "
            "include_final_endpoint."
        )

    if loop_endpoint_policy == "exclude_final_endpoint":
        if source_count < 2:
            raise ValueError(
                "exclude_final_endpoint requires at least two source frames."
            )
        eligible_count = source_count - 1
        if target_count > eligible_count:
            raise ValueError(
                "target_count cannot exceed the source frames before the final "
                "endpoint."
            )
        return [
            _nearest_index(index * eligible_count, target_count)
            for index in range(target_count)
        ]

    if target_count > source_count:
        raise ValueError(
            "target_count cannot exceed source_count when including the final "
            "endpoint."
        )
    if target_count == 1:
        return [0]
    return [
        _nearest_index(index * (source_count - 1), target_count - 1)
        for index in range(target_count)
    ]


def _visual_analysis_frames(image: torch.Tensor) -> torch.Tensor:
    """Return bounded CPU frames for deterministic visual-motion measurement."""

    _, height, width, channels = image.shape
    scale = min(1.0, _ANALYSIS_MAX_EDGE / max(int(height), int(width)))
    analysis_height = max(1, round(int(height) * scale))
    analysis_width = max(1, round(int(width) * scale))
    chunks: list[torch.Tensor] = []

    for start in range(0, int(image.shape[0]), _ANALYSIS_CHUNK_SIZE):
        # Permute is a view. Resize before converting/clamping/premultiplying so the
        # analysis never creates a full-resolution float working copy of the batch.
        chunk = image[start : start + _ANALYSIS_CHUNK_SIZE].detach().permute(
            0, 3, 1, 2
        )
        if (analysis_height, analysis_width) != (int(height), int(width)):
            chunk = functional.interpolate(
                chunk,
                size=(analysis_height, analysis_width),
                mode="bilinear",
                align_corners=False,
                antialias=True,
            )
        chunk = chunk.to(dtype=torch.float32)
        rgb = chunk[:, :3].clamp(0.0, 1.0)
        if channels == 4:
            alpha = chunk[:, 3:4].clamp(0.0, 1.0)
            chunk = torch.cat((rgb * alpha, alpha), dim=1)
        else:
            chunk = rgb
        chunks.append(chunk.cpu())

    return torch.cat(chunks, dim=0)


def visual_motion_sample_indices(
    image: torch.Tensor,
    target_count: int,
    loop_endpoint_policy: str,
) -> tuple[list[int], dict[str, Any]]:
    """Sample equal positions along the batch's measured visual-motion arc."""

    source_count = int(image.shape[0])
    periodic_sample_indices(source_count, target_count, loop_endpoint_policy)
    analysis = _visual_analysis_frames(image)
    motion = (
        analysis[1:].sub(analysis[:-1]).abs().mean(dim=(1, 2, 3))
    )
    cumulative = torch.cat(
        (torch.zeros(1, dtype=motion.dtype), torch.cumsum(motion, dim=0))
    )
    total_motion = float(cumulative[-1])
    if not math.isfinite(total_motion) or total_motion <= 1e-8:
        raise ValueError(
            "visual_motion sampling requires measurable change across the source "
            "frames."
        )

    if loop_endpoint_policy == "exclude_final_endpoint":
        eligible_cumulative = cumulative[:-1]
        target_fractions = [index / target_count for index in range(target_count)]
    else:
        eligible_cumulative = cumulative
        target_fractions = (
            [0.0]
            if target_count == 1
            else [index / (target_count - 1) for index in range(target_count)]
        )

    indices = [
        int(torch.argmin((eligible_cumulative - total_motion * fraction).abs()))
        for fraction in target_fractions
    ]
    if len(set(indices)) != len(indices):
        raise ValueError(
            "visual_motion sampling could not resolve the requested number of "
            "distinct frames; reduce target_count or use timeline sampling."
        )

    return indices, {
        "samplingBasis": "visual_motion",
        "analysis": {
            "maxEdge": _ANALYSIS_MAX_EDGE,
            "metric": "mean_absolute_rgb_or_premultiplied_rgba",
            "totalMotion": total_motion,
            "resizeBackend": str(image.device),
            "scoringBackend": "cpu",
            "determinism": "fixed_resize_backend",
        },
        "targetMotionFractions": target_fractions,
    }


def sample_periodic_image_batch(
    image: Any,
    *,
    target_count: int,
    loop_endpoint_policy: str,
    source_fps: Any,
    intended_fps: Any,
    sampling_basis: str = "timeline",
) -> tuple[torch.Tensor, dict[str, Any]]:
    if not isinstance(image, torch.Tensor):
        raise TypeError("image must be a torch.Tensor IMAGE batch.")
    if image.ndim != 4:
        raise ValueError(
            "image must have rank 4 in [batch, height, width, channels] order."
        )
    source_count, height, width, channels = (int(size) for size in image.shape)
    if source_count < 1:
        raise ValueError("image batch must contain at least one frame.")
    if height < 1 or width < 1:
        raise ValueError(
            "image frames must have positive height and width."
        )
    if channels not in (3, 4):
        raise ValueError("image frames must have 3 (RGB) or 4 (RGBA) channels.")

    resolved_source_fps = _positive_fps(source_fps, "source_fps")
    resolved_intended_fps = _positive_fps(intended_fps, "intended_fps")
    if sampling_basis not in SAMPLING_BASES:
        raise ValueError("sampling_basis must be timeline or visual_motion.")
    if sampling_basis == "timeline":
        indices = periodic_sample_indices(
            source_count,
            target_count,
            loop_endpoint_policy,
        )
        basis_receipt: dict[str, Any] = {}
    else:
        indices, basis_receipt = visual_motion_sample_indices(
            image,
            target_count,
            loop_endpoint_policy,
        )
    index_tensor = torch.tensor(indices, dtype=torch.long, device=image.device)
    sampled = image.index_select(0, index_tensor)
    receipt = {
        "schema": PERIODIC_SAMPLER_RECEIPT_SCHEMA,
        "sourceFrameCount": source_count,
        "targetFrameCount": target_count,
        "loopEndpointPolicy": loop_endpoint_policy,
        "sourceFps": resolved_source_fps,
        "intendedFps": resolved_intended_fps,
        "sourceEndpointSpanSeconds": (source_count - 1) / resolved_source_fps,
        "sourcePlaybackDurationSeconds": source_count / resolved_source_fps,
        "intendedPlaybackDurationSeconds": target_count / resolved_intended_fps,
        "indices": indices,
    }
    receipt.update(basis_receipt)
    return sampled, receipt


def _preview_indices(frame_count: int) -> list[int]:
    if frame_count <= _MAX_PREVIEWS:
        return list(range(frame_count))
    return [
        _nearest_index(index * (frame_count - 1), _MAX_PREVIEWS - 1)
        for index in range(_MAX_PREVIEWS)
    ]


class LF_PeriodicImageBatchSampler:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": (
                            "Ordered IMAGE batch to sample without interpolation or "
                            "pixel conversion."
                        )
                    },
                ),
                "target_count": (
                    Input.INTEGER,
                    {
                        "default": 24,
                        "min": 1,
                        "max": 4096,
                        "step": 1,
                        "tooltip": "Exact number of output frames.",
                    },
                ),
                "loop_endpoint_policy": (
                    LOOP_ENDPOINT_POLICIES,
                    {
                        "default": "exclude_final_endpoint",
                        "tooltip": (
                            "Omit the source's final endpoint from the sampled batch, "
                            "or include it. For a closed loop, reuse the opening frame "
                            "as the ending endpoint before choosing omit."
                        ),
                    },
                ),
                "source_fps": (
                    Input.FLOAT,
                    {
                        "default": 24.0,
                        "min": 0.01,
                        "max": 1000.0,
                        "step": 0.01,
                        "tooltip": (
                            "Source timing recorded in the receipt; sampling is "
                            "governed by exact frame counts."
                        ),
                    },
                ),
                "intended_fps": (
                    Input.FLOAT,
                    {
                        "default": 12.0,
                        "min": 0.01,
                        "max": 1000.0,
                        "step": 0.01,
                        "tooltip": "Intended playback rate recorded in the receipt.",
                    },
                ),
            },
            "optional": {
                # Keep the original positional widget first. Older workflows may not
                # carry widgets_values_named, so new controls must append after it.
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
                "sampling_basis": (
                    SAMPLING_BASES,
                    {
                        "default": "timeline",
                        "tooltip": (
                            "Timeline uses equal frame intervals. Visual motion uses "
                            "equal points along the measured image-change arc, which "
                            "compensates for pauses and uneven movement."
                        ),
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Exactly target_count source frames selected by lossless tensor indexing.",
        "Sampling indices and source/intended timing receipt.",
        "Individual sampled frames in output order.",
    )
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "receipt", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)

    def on_exec(
        self,
        image: torch.Tensor,
        target_count: int,
        loop_endpoint_policy: str,
        source_fps: float,
        intended_fps: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        sampling_basis = (
            normalize_list_to_value(kwargs["sampling_basis"])
            if "sampling_basis" in kwargs
            else "timeline"
        )
        sampled, receipt = sample_periodic_image_batch(
            image,
            target_count=target_count,
            loop_endpoint_policy=loop_endpoint_policy,
            source_fps=source_fps,
            intended_fps=intended_fps,
            sampling_basis=sampling_basis,
        )

        displayed_indices = _preview_indices(int(sampled.shape[0]))
        nodes: list[dict[str, Any]] = []
        dataset = {"nodes": nodes}
        for masonry_index, output_frame_index in enumerate(displayed_indices):
            frame = sampled[output_frame_index].unsqueeze(0)
            preview = cache_generated_preview(frame)
            node = create_masonry_node(
                f"Output frame {output_frame_index}",
                preview.url,
                masonry_index,
            )
            node["cells"]["lfImage"]["htmlProps"]["title"] = (
                f"Output frame {output_frame_index}"
            )
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
            "periodicimagebatchsampler",
            payload,
            normalize_list_to_value(kwargs.get("node_id")),
        )
        _, image_list = normalize_output_image(sampled)
        return {
            "ui": {"lf_output": [payload]},
            "result": (sampled, receipt, image_list),
        }


NODE_CLASS_MAPPINGS = {
    "LF_PeriodicImageBatchSampler": LF_PeriodicImageBatchSampler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_PeriodicImageBatchSampler": "Periodic image batch sampler",
}
