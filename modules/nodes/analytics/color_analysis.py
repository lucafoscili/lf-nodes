import numpy as np
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import BLUE_CHANNEL_ID, EVENT_PREFIX, FUNCTION, GREEN_CHANNEL_ID, Input, INTENSITY_ID, RED_CHANNEL_ID
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
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list", "dataset")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON)

    def on_exec(self, **kwargs: dict):
        source_image: list[torch.Tensor] = normalize_input_image(kwargs.get("source_image", []))
        target_image: list[torch.Tensor] = normalize_input_image(kwargs.get("target_image", []))

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
                "red_channel": self.generate_mapping(target_histograms[RED_CHANNEL_ID], source_histograms[RED_CHANNEL_ID]),
                "green_channel": self.generate_mapping(target_histograms[GREEN_CHANNEL_ID], source_histograms[GREEN_CHANNEL_ID]),
                "blue_channel": self.generate_mapping(target_histograms[BLUE_CHANNEL_ID], source_histograms[BLUE_CHANNEL_ID]),
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

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}coloranalysis", {
            "node": kwargs.get("node_id"),
            "datasets": mapping_datasets
        })

        image_batch, image_list = normalize_output_image(target_image)

        return (image_batch[0], image_list, mapping_datasets)

    @staticmethod
    def generate_mapping(target_hist, source_hist):
        source_cdf = np.cumsum(source_hist).astype(np.float64)
        source_cdf /= source_cdf[-1]
        target_cdf = np.cumsum(target_hist).astype(np.float64)
        target_cdf /= target_cdf[-1]

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