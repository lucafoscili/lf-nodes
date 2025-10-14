import re

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.logic.split_svgs import split_svgs

# region LF_ViewSVGs
class LF_ViewSVGs:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "svg_string": (Input.STRING, {
                    "tooltip": "A string containing one or more <svg>...</svg> blocks concatenated together."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (False, False)
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("svg_string", "svg_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        svg_string: str = kwargs.get("svg_string", "") or ""

        svg_blocks = split_svgs(svg_string)

        nodes: list[dict] = []
        for index, _ in enumerate(svg_blocks):
            slot_name = f"slot-{index}"
            nodes.append({
                "cells": {
                    "lfSlot": {
                        "shape": "slot",
                        "value": slot_name
                    }
                },
                "id": str(index),
                "value": str(index)
            })

        dataset: dict = { "nodes": nodes }

        slot_names = [f"slot-{i}" for i in range(len(svg_blocks))]
        slot_map = { name: svg for name, svg in zip(slot_names, svg_blocks) }

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}viewsvgs", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
            "slot_map": slot_map,
        })

        return (svg_string, svg_blocks)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ViewSVGs": LF_ViewSVGs,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ViewSVGs": "View SVGs",
}
# endregion
