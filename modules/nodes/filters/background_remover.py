from __future__ import annotations

from typing import Any, Dict, List

import torch
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import apply_background_remover_filter
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_image,
)
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.ui import create_compare_node

# region LF_BackgroundRemover
class LF_BackgroundRemover:
    @classmethod
    def INPUT_TYPES(cls):
        models = [
            "u2net",
            "u2netp",
            "u2net_human_seg",
            "silueta",
            "isnet-general-use",
            "isnet-anime",
        ]
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {"tooltip": "Input image tensor or list of tensors."},
                ),
                "transparent_background": (
                    Input.BOOLEAN,
                    {
                        "default": True,
                        "tooltip": "When enabled, keep the background transparent instead of filling it with the chosen color.",
                    },
                ),
                "background_color": (
                    Input.STRING,
                    {
                        "default": "#000000",
                        "tooltip": "Hex color used when transparency is disabled (e.g. #FFFFFF).",
                    },
                ),
                "model": (
                    models,
                    {
                        "default": "u2net",
                        "tooltip": "rembg ONNX model to use for matting.",
                    },
                ),
            },
            "optional": {
                "ui_widget": (
                    Input.LF_COMPARE,
                    {"default": {}},
                ),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("IMAGE", "IMAGE", "MASK", "JSON")
    RETURN_NAMES = ("image", "cutout", "mask", "stats")
    INPUT_IS_LIST = (True, False, False, False, False)
    OUTPUT_IS_LIST = (False, True, False, False)

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        images = normalize_input_image(kwargs.get("image"))
        if not images:
            raise RuntimeError("No images provided for background removal.")

        transparent = normalize_list_to_value(kwargs.get("transparent_background"))
        if transparent is None:
            transparent = True

        background_color = normalize_list_to_value(kwargs.get("background_color")) or "#000000"
        model = str(normalize_list_to_value(kwargs.get("model")) or "u2net")

        settings = {
            "transparent_background": transparent,
            "color": background_color,
            "model": model,
        }

        nodes: List[dict] = []
        dataset: Dict[str, Any] = {"nodes": nodes}
        payloads: List[Dict[str, Any]] = []

        def run_filter(image: torch.Tensor, *, settings=settings) -> torch.Tensor:
            result_image, payload = apply_background_remover_filter(image, settings)
            payloads.append(payload)
            return result_image

        processed_images = process_and_save_image(
            images=images,
            filter_function=run_filter,
            filter_args={},
            filename_prefix="background_remover",
            nodes=nodes,
        )

        cutout_images: List[torch.Tensor] = []
        mask_images: List[torch.Tensor] = []
        stats_rows: List[dict] = []

        for index, payload in enumerate(payloads):
            cutout_tensor = payload.get("cutout_tensor")
            mask_tensor = payload.get("mask_tensor")
            if cutout_tensor is None or mask_tensor is None:
                raise RuntimeError("Background remover filter response missing required tensors.")

            cutout_images.append(cutout_tensor)
            mask_images.append(mask_tensor)

            stats = dict(payload.get("stats", {})) if payload.get("stats") else {}
            stats["index"] = index
            stats_rows.append(stats)

            cutout_url = payload.get("cutout")
            mask_url = payload.get("mask")
            if cutout_url and mask_url:
                nodes.append(create_compare_node(cutout_url, mask_url, len(nodes)))

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}backgroundremover",
            {"node": node_id, "dataset": dataset},
        )

        composite_batches, composite_list = normalize_output_image(processed_images)
        _, cutout_list = normalize_output_image(cutout_images)

        mask_for_grouping = [mask.unsqueeze(-1) for mask in mask_images]
        mask_batches, _ = normalize_output_image(mask_for_grouping)
        mask_output = mask_batches[0].squeeze(-1) if mask_batches else mask_images[0]

        stats_output = {"runs": stats_rows}

        primary_image = composite_batches[0] if composite_batches else processed_images[0]

        return (
            primary_image,
            cutout_list,
            mask_output,
            stats_output,
        )
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_BackgroundRemover": LF_BackgroundRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_BackgroundRemover": "Background Remover",
}
# endregion