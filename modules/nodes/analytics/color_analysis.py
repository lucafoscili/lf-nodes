import numpy as np
import torch

from . import CATEGORY
from ...utils.constants import BLUE_CHANNEL_ID, FUNCTION, GREEN_CHANNEL_ID, Input, INTENSITY_ID, RED_CHANNEL_ID
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.conversion import tensor_to_numpy
from ...utils.helpers.logic import normalize_input_image, normalize_output_image

# region LF_ColorAnalysis
class LF_ColorAnalysis:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "source_image": (Input.IMAGE, {
                    "tooltip": "Source image from which to extract the color style."
                }),
                "target_image": (Input.IMAGE, {
                    "tooltip": "Target image to be adjusted to match the source color pattern."
                }),
            },
            "optional": {
                "preset": (Input.COMBO, {
                    "default": "balanced",
                    "options": ["balanced", "skin_priority", "highlight_safe", "full_matching", "simple"],
                    "tooltip": "balanced: Moderate skin protection and highlight reduction for mixed lighting.\nskin_priority: Strong skin tone protection with moderate highlight reduction.\nhighlight_safe: Minimal highlight influence with balanced skin protection.\nfull_matching: Standard histogram matching without selective weighting.\nsimple: Same as full_matching, original behavior."
                }),
                "ui_widget": (Input.LF_TAB_BAR_CHART, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False)
    OUTPUT_TOOLTIPS = (
        "Image tensor adjusted to match the source color pattern.",
        "List of image tensors adjusted to match the source color pattern.",
        "JSON object with mapping information."
    )
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list", "dataset")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON)

    def on_exec(self, **kwargs: dict):
        source_image: list[torch.Tensor] = normalize_input_image(kwargs.get("source_image", []))
        target_image: list[torch.Tensor] = normalize_input_image(kwargs.get("target_image", []))
        preset: str = str(kwargs.get("preset", "balanced") or "balanced").lower()

        # Set parameters based on preset
        if preset == "balanced":
            selective_matching = True
            skin_protection = 0.7
            highlight_reduction = 0.3
        elif preset == "skin_priority":
            selective_matching = True
            skin_protection = 0.9
            highlight_reduction = 0.5
        elif preset == "highlight_safe":
            selective_matching = True
            skin_protection = 0.5
            highlight_reduction = 0.1
        elif preset == "full_matching":
            selective_matching = False
            skin_protection = 1.0
            highlight_reduction = 1.0
        elif preset == "simple":
            selective_matching = False
            skin_protection = 1.0
            highlight_reduction = 1.0
        else:
            # Fallback to balanced
            selective_matching = True
            skin_protection = 0.7
            highlight_reduction = 0.3

        if not source_image or not target_image:
            raise ValueError("Source and target images are required")

        if len(source_image) != len(target_image):
            raise ValueError("Source and Target batches should have the same number of images.")

        mapping_datasets: dict = {}

        for idx in range(len(source_image)):
            source_np = tensor_to_numpy(source_image[idx])
            target_np = tensor_to_numpy(target_image[idx])

            source_histograms: dict = {
                RED_CHANNEL_ID: np.histogram(source_np[:, :, 0], bins=256, range=(0, 256))[0],
                GREEN_CHANNEL_ID: np.histogram(source_np[:, :, 1], bins=256, range=(0, 256))[0],
                BLUE_CHANNEL_ID: np.histogram(source_np[:, :, 2], bins=256, range=(0, 256))[0]
            }

            target_histograms: dict = {
                RED_CHANNEL_ID: np.histogram(target_np[:, :, 0], bins=256, range=(0, 256))[0],
                GREEN_CHANNEL_ID: np.histogram(target_np[:, :, 1], bins=256, range=(0, 256))[0],
                BLUE_CHANNEL_ID: np.histogram(target_np[:, :, 2], bins=256, range=(0, 256))[0]
            }

            mapping_json: dict = {
                "red_channel": self.generate_mapping(target_histograms[RED_CHANNEL_ID], source_histograms[RED_CHANNEL_ID], skin_protection, highlight_reduction),
                "green_channel": self.generate_mapping(target_histograms[GREEN_CHANNEL_ID], source_histograms[GREEN_CHANNEL_ID], skin_protection, highlight_reduction),
                "blue_channel": self.generate_mapping(target_histograms[BLUE_CHANNEL_ID], source_histograms[BLUE_CHANNEL_ID], skin_protection, highlight_reduction),
            }

            nodes: list[dict] = []
            dataset: dict = {
                "columns": [
                    {"id": INTENSITY_ID, "title": "Color Intensity (From)"},
                    {"id": RED_CHANNEL_ID, "title": "Red Channel Mapping", "shape": "number"},
                    {"id": GREEN_CHANNEL_ID, "title": "Green Channel Mapping", "shape": "number"},
                    {"id": BLUE_CHANNEL_ID, "title": "Blue Channel Mapping", "shape": "number"}
                ],
                "nodes": nodes
            }

            for i in range(256):
                node: dict = {
                    "id": str(i),
                    "cells": {
                        INTENSITY_ID: {"value": str(i)},
                        RED_CHANNEL_ID: {"value": str(mapping_json["red_channel"][i]), "shape": "number"},
                        GREEN_CHANNEL_ID: {"value": str(mapping_json["green_channel"][i]), "shape": "number"},
                        BLUE_CHANNEL_ID: {"value": str(mapping_json["blue_channel"][i]), "shape": "number"}
                    }
                }
                nodes.append(node)

            mapping_datasets[f"Image #{idx + 1}"] = dataset

        safe_send_sync("coloranalysis", {
            "datasets": mapping_datasets
        }, kwargs.get("node_id"))

        image_batch, image_list = normalize_output_image(target_image)

        # Handle empty input case
        if not image_batch:
            return None, [], {}

        return (image_batch[0], image_list, mapping_datasets)

    @staticmethod
    def generate_mapping(target_hist, source_hist, skin_protection=0.7, highlight_reduction=0.3):
        """
        Generate histogram mapping with optional selective weighting for skin tone protection.

        Args:
            target_hist: Target image histogram
            source_hist: Source image histogram
            skin_protection: How much to protect skin tone range (0.0-1.0, higher = more protection)
            highlight_reduction: How much to reduce highlight influence (0.0-1.0, lower = less influence)
        """
        # If both protection parameters are 1.0, use original simple histogram matching
        if skin_protection == 1.0 and highlight_reduction == 1.0:
            source_cdf = np.cumsum(source_hist).astype(np.float64)
            source_cdf /= source_cdf[-1]
            target_cdf = np.cumsum(target_hist).astype(np.float64)
            target_cdf /= target_cdf[-1]

            mapping = np.zeros(256, dtype=np.uint8)
            for r in range(256):
                s = np.argmin(np.abs(source_cdf - target_cdf[r]))
                mapping[r] = s
            return mapping.tolist()

        # Create weighted histograms to reduce highlight influence and protect skin tones
        source_weights = np.ones(256)
        target_weights = np.ones(256)

        # Reduce influence of very bright highlights (potential windows/artificial lights)
        highlight_mask = np.arange(256) > 200
        source_weights[highlight_mask] *= highlight_reduction
        target_weights[highlight_mask] *= highlight_reduction

        # Protect midtone skin tone range (roughly 100-180 in 0-255 range)
        skin_mask = (np.arange(256) >= 100) & (np.arange(256) <= 180)
        source_weights[skin_mask] *= skin_protection
        target_weights[skin_mask] *= skin_protection

        # Apply weights to histograms
        weighted_source_hist = source_hist.astype(np.float64) * source_weights
        weighted_target_hist = target_hist.astype(np.float64) * target_weights

        # Create CDFs from weighted histograms
        source_cdf = np.cumsum(weighted_source_hist)
        source_cdf /= source_cdf[-1] if source_cdf[-1] > 0 else 1

        target_cdf = np.cumsum(weighted_target_hist)
        target_cdf /= target_cdf[-1] if target_cdf[-1] > 0 else 1

        mapping = np.zeros(256, dtype=np.uint8)

        for r in range(256):
            s = np.argmin(np.abs(source_cdf - target_cdf[r]))
            mapping[r] = s
        return mapping.tolist()
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ColorAnalysis": LF_ColorAnalysis,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ColorAnalysis": "Color Analysis",
}
# endregion
