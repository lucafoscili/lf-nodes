from __future__ import annotations

from typing import List

import numpy as np
import torch
from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters.background_remover import (
    apply_background_removal,
    normalize_hex_color,
)
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import convert_to_boolean, tensor_to_pil
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_image,
)
from ...utils.helpers.ui import create_compare_node

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
        images = normalize_input_image(kwargs.get("image"))
        if not images:
            raise RuntimeError("No images provided for background removal.")

        transparent_raw = normalize_list_to_value(kwargs.get("transparent_background"))
        transparent = convert_to_boolean(
            transparent_raw if transparent_raw is not None else True
        )
        if transparent is None:
            transparent = True

        background_color = normalize_hex_color(
            normalize_list_to_value(kwargs.get("background_color")) or "#000000"
        )
        model = str(normalize_list_to_value(kwargs.get("model")) or "u2net")

        composite_images: List[torch.Tensor] = []
        cutout_images: List[torch.Tensor] = []
        mask_images: List[torch.Tensor] = []
        stats_rows: List[dict] = []
        compare_nodes: List[dict] = []

        for index, image in enumerate(images):
            result = apply_background_removal(
                image,
                transparent_background=transparent,
                background_color=background_color,
                model_name=model,
            )

            composite_images.append(result.composite)
            cutout_images.append(result.cutout)
            mask_images.append(result.mask)

            image_stats = dict(result.stats)
            image_stats["index"] = index
            stats_rows.append(image_stats)

            source_pil = tensor_to_pil(image)
            source_path, source_subfolder, source_filename = resolve_filepath(
                filename_prefix="background_src",
                image=image,
            )
            source_pil.save(source_path, format="PNG")
            source_url = get_resource_url(source_subfolder, source_filename, "temp")

            composite_pil = tensor_to_pil(result.composite)
            composite_path, composite_subfolder, composite_filename = resolve_filepath(
                filename_prefix="background_result",
            )
            composite_pil.save(composite_path, format="PNG")
            composite_url = get_resource_url(
                composite_subfolder, composite_filename, "temp"
            )
            compare_nodes.append(create_compare_node(source_url, composite_url, len(compare_nodes)))

            cutout_pil = tensor_to_pil(result.cutout)
            cutout_path, cutout_subfolder, cutout_filename = resolve_filepath(
                filename_prefix="background_cutout",
            )
            cutout_pil.save(cutout_path, format="PNG")
            cutout_url = get_resource_url(cutout_subfolder, cutout_filename, "temp")

            mask_np = (result.mask.squeeze(0).cpu().numpy() * 255).astype(np.uint8)
            mask_image = Image.fromarray(mask_np, mode="L")
            mask_path, mask_subfolder, mask_filename = resolve_filepath(
                filename_prefix="background_mask",
            )
            mask_image.save(mask_path, format="PNG")
            mask_url = get_resource_url(mask_subfolder, mask_filename, "temp")
            compare_nodes.append(create_compare_node(cutout_url, mask_url, len(compare_nodes)))

        dataset = {"nodes": compare_nodes}
        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}backgroundremover",
            {"node": kwargs.get("node_id"), "dataset": dataset},
        )

        composite_batches, composite_list = normalize_output_image(composite_images)
        cutout_batches, cutout_list = normalize_output_image(cutout_images)
        mask_for_grouping = [mask.unsqueeze(-1) for mask in mask_images]
        mask_batches, _ = normalize_output_image(mask_for_grouping)
        mask_output = (
            mask_batches[0].squeeze(-1)
            if mask_batches
            else mask_images[0]
        )

        stats_output = {"runs": stats_rows}

        primary_image = composite_batches[0] if composite_batches else composite_images[0]
        primary_cutout = cutout_batches[0] if cutout_batches else cutout_images[0]

        return (
            primary_image,
            cutout_list,
            mask_output,
            stats_output,
        )


NODE_CLASS_MAPPINGS = {
    "LF_BackgroundRemover": LF_BackgroundRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_BackgroundRemover": "Background Remover",
}
