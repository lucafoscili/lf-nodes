from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

# region LF_KeywordCounter
class LF_KeywordCounter:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "prompt": (Input.STRING, {
                    "multiline": True, 
                    "tooltip": "Prompt containing keywords to count."
                }),
                "separator": (Input.STRING, {
                    "default": ", ", 
                    "tooltip": "Character(s) used to separate keywords in the prompt."
                }),
            },
            "optional": {
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
    OUTPUT_NODE = True
    RETURN_NAMES = ("chart_dataset", "chip_dataset")
    RETURN_TYPES = ("JSON", "JSON")

    def on_exec(self, **kwargs: dict):
        prompt: str = normalize_list_to_value(kwargs.get("prompt"))
        separator: str = normalize_list_to_value(kwargs.get("separator"))

        keywords: list[str] = prompt.split(separator)
        keyword_count: dict = {}

        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword:
                keyword_count[keyword] = keyword_count.get(keyword, 0) + 1

        chart_nodes: list[dict] = []
        chart_dataset: dict = {
            "columns": [
                {"id": "Axis_0", "title": "Keyword"},
                {"id": "Series_0", "shape": "number", "title": "Count"},
            ],
            "nodes": chart_nodes
        }

        for idx, (keyword, count) in enumerate(keyword_count.items()):
            node = {
                "cells": {
                    "Axis_0": {"value": keyword},
                    "Series_0": {"value": count},
                },
                "id": str(idx)
            }
            chart_nodes.append(node)

        chip_nodes: list[dict] = []
        chip_dataset: dict = {
            "nodes": chip_nodes
        }

        for keyword in keyword_count:
            node = {
                "id": keyword,
                "value": keyword
            }
            chip_nodes.append(node)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}keywordcounter", {
            "node": kwargs.get("node_id"),
            "datasets": {
                "chart": chart_dataset,
                "chip": chip_dataset,
            }
        })

        return (chart_dataset, chip_dataset)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_KeywordCounter": LF_KeywordCounter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_KeywordCounter": "Keyword counter",
}
# endregion