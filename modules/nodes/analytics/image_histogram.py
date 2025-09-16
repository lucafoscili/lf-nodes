import numpy as np
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import BLUE_CHANNEL_ID, EVENT_PREFIX, FUNCTION, GREEN_CHANNEL_ID, Input, INTENSITY_ID, RED_CHANNEL_ID, SUM_ID
from ...utils.helpers import normalize_input_image, normalize_output_image

# region LF_ImageHistogram
class LF_ImageHistogram:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input images to generate histograms from."
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
    RETURN_TYPES = ("IMAGE", "IMAGE", "JSON")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image", []))

        batch_histograms: list[dict] = []
        datasets: dict = {}

        for img in image:
            image_batch_np = img.cpu().numpy() * 255.0
            image_batch_np = image_batch_np.astype(np.uint8)

            for i in range(image_batch_np.shape[0]):
                image_np = image_batch_np[i]

                red_channel = image_np[:, :, 0]
                green_channel = image_np[:, :, 1]
                blue_channel = image_np[:, :, 2]

                r = np.histogram(red_channel, bins=256, range=(0, 255))[0]
                g = np.histogram(green_channel, bins=256, range=(0, 255))[0]
                b = np.histogram(blue_channel, bins=256, range=(0, 255))[0]

                sum_channel = red_channel.astype(np.int32) + green_channel.astype(np.int32) + blue_channel.astype(np.int32)
                s = np.histogram(sum_channel, bins=256, range=(0, 765))[0]

                batch_histograms.append({
                    "r": r.tolist(),
                    "g": g.tolist(),
                    "b": b.tolist(),
                    "s": s.tolist(),
                })

        for index, hist in enumerate(batch_histograms):
            nodes: list[dict] = []
            dataset: dict = {
                "columns": [
                    {"id": INTENSITY_ID, "title": "Intensity"},
                    {"id": RED_CHANNEL_ID, "shape": "number", "title": "Red Channel"},
                    {"id": GREEN_CHANNEL_ID, "shape": "number", "title": "Green Channel"},
                    {"id": BLUE_CHANNEL_ID, "shape": "number", "title": "Blue Channel"},
                    {"id": SUM_ID, "shape": "number", "title": "Sum of Channels"},
                ],
                "nodes": nodes
            }

            for i in range(256):
                node: dict = {
                    "cells": {
                        INTENSITY_ID: {"value": i},
                        RED_CHANNEL_ID: {"value": hist["r"][i]},
                        GREEN_CHANNEL_ID: {"value": hist["g"][i]},
                        BLUE_CHANNEL_ID: {"value": hist["b"][i]},
                        SUM_ID: {"value": hist["s"][i] if i < len(hist["s"]) else 0},
                    },
                    "id": str(i),
                }
                nodes.append(node)

            datasets[f"Image #{index + 1}"] = dataset

        b, l = normalize_output_image(image)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imagehistogram", {
            "node": kwargs.get("node_id"), 
            "datasets": datasets,
        })

        return (b[0], l, datasets)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImageHistogram": LF_ImageHistogram,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageHistogram":  "Image Histogram",
}
# endregion