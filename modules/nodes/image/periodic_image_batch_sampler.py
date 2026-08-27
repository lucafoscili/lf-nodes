from __future__ import annotations

import math
from typing import Any

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath, safe_send_sync
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import normalize_list_to_value
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.ui import create_masonry_node


PERIODIC_SAMPLER_RECEIPT_SCHEMA = "lf.periodic_image_batch_sampler.receipt.v1"
LOOP_ENDPOINT_POLICIES = ["exclude_final_endpoint", "include_final_endpoint"]
_MAX_PREVIEWS = 64


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


def sample_periodic_image_batch(
    image: Any,
    *,
    target_count: int,
    loop_endpoint_policy: str,
    source_fps: Any,
    intended_fps: Any,
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

    indices = periodic_sample_indices(
        source_count,
        target_count,
        loop_endpoint_policy,
    )
    resolved_source_fps = _positive_fps(source_fps, "source_fps")
    resolved_intended_fps = _positive_fps(intended_fps, "intended_fps")
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
    return sampled, receipt


def _preview_indices(frame_count: int) -> list[int]:
    if frame_count <= _MAX_PREVIEWS:
        return list(range(frame_count))
    return [
        _nearest_index(index * (frame_count - 1), _MAX_PREVIEWS - 1)
        for index in range(_MAX_PREVIEWS)
    ]


class LF_PeriodicImageBatchSampler:
    def __init__(self):
        self._temp_cache = TempFileCache()

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
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Exactly target_count source frames selected by lossless tensor indexing.",
        "Sampling indices and source/intended timing receipt.",
    )
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "receipt")
    RETURN_TYPES = (Input.IMAGE, Input.JSON)

    def on_exec(
        self,
        image: torch.Tensor,
        target_count: int,
        loop_endpoint_policy: str,
        source_fps: float,
        intended_fps: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self._temp_cache.cleanup()
        sampled, receipt = sample_periodic_image_batch(
            image,
            target_count=target_count,
            loop_endpoint_policy=loop_endpoint_policy,
            source_fps=source_fps,
            intended_fps=intended_fps,
        )

        displayed_indices = _preview_indices(int(sampled.shape[0]))
        nodes: list[dict[str, Any]] = []
        dataset = {"nodes": nodes}
        for masonry_index, output_frame_index in enumerate(displayed_indices):
            frame = sampled[output_frame_index].unsqueeze(0)
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix="periodic_image_batch_sampler",
                image=frame,
                temp_cache=self._temp_cache,
            )
            tensor_to_pil(frame).save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")
            node = create_masonry_node(filename, url, masonry_index)
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
        return {
            "ui": {"lf_output": [payload]},
            "result": (sampled, receipt),
        }


NODE_CLASS_MAPPINGS = {
    "LF_PeriodicImageBatchSampler": LF_PeriodicImageBatchSampler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_PeriodicImageBatchSampler": "Periodic image batch sampler",
}
