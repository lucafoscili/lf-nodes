import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value

# region LF_CaptionImageWD14
class LF_CaptionImageWD14:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tagger": (
                    Input.TAGGER,
                    {
                        "tooltip": "WD14 TAGGER object (ONNX or HF/timm).",
                    },
                ),
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": "Image tensor to caption.",
                    },
                ),
            },
            "optional": {
                "show_probabilities": (
                    Input.BOOLEAN,
                    {
                        "default": False,
                        "tooltip": "If true, include probabilities next to tags in the console-style caption.",
                    },
                ),
                "prefix": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": "Prefix to add to each caption.",
                    },
                ),
                "suffix": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": "Suffix to add to each caption.",
                    },
                ),
                "ui_widget": (
                    Input.LF_COUNT_BAR_CHART,
                    {
                        "default": {},
                    },
                ),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True, False, False)
    OUTPUT_TOOLTIPS = (
        "Caption string or list of caption strings.",
        "List of caption strings.",
        "JSON object with additional metadata.",
        "List of JSON objects with additional metadata.",
        "Chart dataset for visualization.",
        "Chip dataset for visualization.",
    )
    RETURN_NAMES = (
        "string",
        "string_list",
        "json",
        "json_list",
        "chart_dataset",
        "chip_dataset",
    )
    RETURN_TYPES = (
        Input.STRING,
        Input.STRING,
        Input.JSON,
        Input.JSON,
        Input.JSON,
        Input.JSON,
    )

    def on_exec(self, **kwargs: dict):
        images = normalize_input_image(kwargs["image"])
        tagger = normalize_list_to_value(kwargs["tagger"])
        show_probabilities = bool(normalize_list_to_value(kwargs.get("show_probabilities", False)))
        prefix = normalize_list_to_value(kwargs.get("prefix", ""))
        suffix = normalize_list_to_value(kwargs.get("suffix", ""))

        if tagger is None or not hasattr(tagger, "tag"):
            raise ValueError("Provided TAGGER input is not a valid WD14 tagger.")

        string_list: list[str] = []
        pairs_list: list[list[tuple[str, float]]] = []
        chart_nodes: list[dict] = []
        chip_nodes: list[dict] = []
        chart_dataset: dict = {
            "columns": [
                {"id": "Axis_0", "title": "Tag"},
            ],
            "nodes": chart_nodes,
        }
        chip_dataset: dict = {
            "nodes": chip_nodes,
        }

        for idx, img_tensor in enumerate(images):
            if isinstance(img_tensor, torch.Tensor):
                pairs = tagger.tag(img_tensor)
            else:
                pairs = tagger.tag(img_tensor)

            tags = [tag for tag, _ in pairs]

            for tag, conf in pairs:
                conf_rounded = round(float(conf), 3)
                chart_node = {
                    "cells": {
                        "Axis_0": {"value": tag},
                        "Series_0": {"value": conf_rounded},
                    },
                    "id": tag,
                }
                chip_node = {
                    "id": tag,
                    "title": "Confidence: {:.2f}".format(conf_rounded),
                    "value": tag,
                }

                chart_nodes.append(chart_node)
                chip_nodes.append(chip_node)

            pairs_list.append(pairs)

            caption_body = ", ".join(tags)
            if show_probabilities and pairs:
                caption_body = ", ".join(
                    f"{tag} ({conf:.2f})" for tag, conf in pairs
                )

            if prefix:
                caption_body = f"{prefix}, {caption_body}" if caption_body else prefix
            if suffix:
                caption_body = f"{caption_body}, {suffix}" if caption_body else suffix

            string_list.append(caption_body)

        safe_send_sync(
            "captionimagewd14onnx",
            {
                "datasets": {
                    "chart": chart_dataset,
                    "chip": chip_dataset,
                }
            },
            kwargs.get("node_id"),
        )

        string_o = string_list[0] if len(string_list) == 1 else string_list
        pairs_o = pairs_list[0] if len(pairs_list) == 1 else pairs_list

        if len(string_list) > 1:
            tag_counts: dict[str, int] = {}
            for pairs in pairs_list:
                for tag, _ in pairs:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

            chart_nodes = []
            chip_nodes = []
            for tag, count in tag_counts.items():
                chart_node = {
                    "cells": {
                        "Axis_0": {"value": tag},
                        "Series_0": {"value": count},
                    },
                    "id": tag,
                }
                chart_nodes.append(chart_node)

                chip_node = {
                    "id": tag,
                    "title": "Count: {}".format(count),
                    "value": tag,
                }
                chip_nodes.append(chip_node)

            chart_dataset["columns"].append(
                {
                    "id": "Series_0",
                    "shape": "number",
                    "title": "Count",
                }
            )
            chart_dataset["nodes"] = chart_nodes
            chip_dataset["nodes"] = chip_nodes

        else:
            chart_dataset["columns"].append(
                {
                    "id": "Series_0",
                    "shape": "number",
                    "title": "Confidence",
                }
            )

        return (string_o, string_list, pairs_o, pairs_list, chart_dataset, chip_dataset)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CaptionImageWD14Onnx": LF_CaptionImageWD14,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CaptionImageWD14Onnx": "Caption Image (WD14, TAGGER)",
}
# endregion
