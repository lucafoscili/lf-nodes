import re

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.logic.split_svgs import split_svgs
from ...utils.helpers.logic import normalize_list_to_value

# region LF_ViewSVGs
class LF_ViewSVGs:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "svg": (Input.STRING, {
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
    OUTPUT_TOOLTIPS = (
        "Pass-through SVG string.",
        "List of pass-through SVG strings.",
    )
    RETURN_NAMES = ("svg", "svg_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        raw = normalize_list_to_value(kwargs.get("svg"))

        if isinstance(raw, bytes):
            try:
                svg_string = raw.decode('utf-8')
            except Exception:
                svg_string = raw.decode('latin-1', errors='ignore')
        else:
            svg_string = str(raw or "")

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
        slot_map = { name: block for name, block in zip(slot_names, svg_blocks) }

        safe_send_sync("viewsvgs", {
            "dataset": dataset,
            "slot_map": slot_map,
        }, kwargs.get("node_id"))

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
