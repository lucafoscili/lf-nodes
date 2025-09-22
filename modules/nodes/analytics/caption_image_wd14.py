import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value
from ...utils.helpers.tagging import build_id2label

#region LF_CaptionImageWD14
class LF_CaptionImageWD14:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "processor": ("*", {
                    "tooltip": "Processor returned by LF_LoadWD14Model.",
                }),
                "model": ("*", {
                    "tooltip": "Model returned by LF_LoadWD14Model.",
                }),
                "image": (Input.IMAGE, {
                    "tooltip": "Image tensor to caption."
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Minimum confidence to keep a tag."
                }),
                "top_k": (Input.INTEGER, {
                    "default": 20,
                    "min": 1,
                    "step": 1,
                    "tooltip": "Maximum number of tags to output."
                }),
                "remove_underscore": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Remove underscores from tags."
                })
            },
            "optional": {
                "blacklist": (Input.STRING, {
                    "default": "",
                    "tooltip": "Comma-separated list of tags to ignore."
                }),
                "prefix": (Input.STRING, {
                    "default": "",
                    "tooltip": "Prefix to add to each caption."
                }),
                "suffix": (Input.STRING, {
                    "default": "",
                    "tooltip": "Suffix to add to each caption."
                }),
                "ui_widget": (Input.LF_COUNT_BAR_CHART, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("string", "string_list", "json", "json_list", "chart_dataset", "chip_dataset")
    RETURN_TYPES = ("STRING", "STRING", "JSON", "JSON", "JSON", "JSON")
    OUTPUT_IS_LIST = (False, True, False, True, False, False)

    def on_exec(self, **kwargs: dict):
        images = normalize_input_image(kwargs["image"])
        processor = normalize_list_to_value(kwargs["processor"])
        model = normalize_list_to_value(kwargs["model"])
        thr = normalize_list_to_value(kwargs["threshold"])
        k = normalize_list_to_value(kwargs["top_k"])
        remove_underscore = normalize_list_to_value(kwargs.get("remove_underscore", True))
        blacklist = normalize_list_to_value(kwargs.get("blacklist", ""))
        prefix = normalize_list_to_value(kwargs.get("prefix", ""))
        suffix = normalize_list_to_value(kwargs.get("suffix", ""))

        string_list: list[str] = []
        pairs_list: list[dict] = []
        chart_nodes: list[dict] = []
        chip_nodes: list[dict] = []
        chart_dataset: dict = {
            "columns": [
                {"id": "Axis_0", "title": "Tag"},
            ],
            "nodes": chart_nodes
        }
        chip_dataset: dict = {
            "nodes": chip_nodes
        }
        raw_blacklist = [
            b.strip().lower().replace("_", " ")
            for b in blacklist.split(",")
            if b.strip()
        ]        

        id2lab = build_id2label(model)

        for idx, img_tensor in enumerate(images):
            pil_img = tensor_to_pil(img_tensor)
            try:
                inputs = processor(images=pil_img, return_tensors="pt") # HF‐style API
            except TypeError:
                try:
                    inputs = processor(pil_img, return_tensors="pt") # positional + return_tensors
                except TypeError:
                    raw = processor(pil_img)  # pure transform
                    if isinstance(raw, torch.Tensor):
                        inputs = {"pixel_values": raw.unsqueeze(0)}
                    elif isinstance(raw, dict):
                        inputs = raw
                    else:
                        raise RuntimeError(f"Unsupported processor output: {type(raw)}")
                    
            with torch.no_grad():
                try:
                    outputs = model(**inputs)
                except TypeError:
                    if isinstance(inputs, dict) and "pixel_values" in inputs:
                        x = inputs["pixel_values"]
                    else:
                        x = next(v for v in inputs.values() if torch.is_tensor(v))
                    outputs = model(x)
                logits = outputs.logits if hasattr(outputs, "logits") else outputs

            probs = logits.sigmoid().cpu().numpy()[0]

            candidates = []
            for i, p in enumerate(probs):
                if p < thr:
                    continue
                tag = id2lab[i]
                if remove_underscore:
                    tag = tag.replace("_", " ")
                candidates.append((tag, float(p)))

            filtered = [
                (tag, conf)
                for tag, conf in candidates
                if tag.lower() not in raw_blacklist
            ]

            filtered.sort(key=lambda x: x[1], reverse=True)
            pairs = filtered[:k]

            tags, _ = zip(*pairs) if len(pairs) > 0 else ([], [])
            for tag in tags:
                conf = pairs[tags.index(tag)][1]
                conf = round(conf, 3)
                chart_node = {
                    "cells": {
                        "Axis_0": {"value": tag},
                        "Series_0": { "value": conf },
                    },
                    "id": tag
                }
                chip_node = {
                    "id": tag,
                    "title": "Confidence: {:.2f}".format(conf),
                    "value": tag,
                }
                
                chart_nodes.append(chart_node)
                chip_nodes.append(chip_node)
            
            pairs_list.append(pairs)
            
            complete_string = f"{prefix + ', ' if prefix else ''}{', '.join(tags)}{', ' + suffix if suffix else ''}"
            string_list.append(complete_string)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}captionimagewd14", {
            "node": kwargs.get("node_id"),
            "datasets": {
                "chart": chart_dataset,
                "chip": chip_dataset,
            }
        })

        string_o = string_list[0] if len(string_list) == 1 else string_list
        pairs_o = pairs_list[0] if len(pairs_list) == 1 else pairs_list

        if len(string_list) > 1:
            tag_counts = {}
            for pairs in pairs_list:
                for tag, conf in pairs:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            chart_nodes = []
            chip_nodes = []
            for tag, count in tag_counts.items():
                chart_node = {
                    "cells": {
                        "Axis_0": {"value": tag},
                        "Series_0": {"value": count},
                    },
                    "id": tag
                }
                chart_nodes.append(chart_node)

                chip_node = {
                    "id": tag,
                    "title": "Count: {}".format(count),
                    "value": tag,
                }
                chip_nodes.append(chip_node)
            
            chart_dataset["columns"].append({
                "id": "Series_0",
                "shape": "number",
                "title": "Count"
            })
            chart_dataset["nodes"] = chart_nodes
            chip_dataset["nodes"] = chip_nodes
            
        else:
            chart_dataset["columns"].append({
                "id": "Series_0",
                "shape": "number",
                "title": "Confidence"
            })

        return (string_o, string_list, pairs_o, pairs_list, chart_dataset, chip_dataset)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CaptionImageWD14": LF_CaptionImageWD14,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CaptionImageWD14": "Caption Image (WD14)",
}
# endregion