from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.logic import normalize_list_to_value, split_svgs

# region LF_SaveSVG
class LF_SaveSVG:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "svg": (Input.STRING, {
                    "tooltip": "SVG data to save (.svg)."
                }),
                "filename_prefix": (Input.STRING, {
                    "default": '', 
                    "tooltip": "Path and filename for saving the SVG. Use slashes to set directories."
                }),
                "add_timestamp": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Add timestamp to the filename as a suffix."
                }),
                "add_counter": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Add a counter to the filename to avoid overwriting."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                }),
            },
            "hidden": { 
                "node_id": "UNIQUE_ID",
            } 
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_NAMES = ("svg",)
    RETURN_TYPES = (Input.STRING,)

    def on_exec(self, **kwargs: dict):
        svg: dict = normalize_list_to_value(kwargs.get("svg"))
        filename_prefix: str = normalize_list_to_value(kwargs.get("filename_prefix"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))
        add_counter: bool = normalize_list_to_value(kwargs.get("add_counter"))

        svg_blocks = split_svgs(svg)

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

            output_file, _, _ = resolve_filepath(
                filename_prefix=filename_prefix,
                base_output_path=get_comfy_dir("output"),
                add_timestamp=add_timestamp,
                extension="svg",
                add_counter=add_counter
            )

            with open(output_file, 'w', encoding='utf-8') as svg_file:
                svg_file.write(svg)

        dataset: dict = { "nodes": nodes }

        slot_names = [f"slot-{i}" for i in range(len(svg_blocks))]
        slot_map = { name: svg for name, svg in zip(slot_names, svg_blocks) }

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}savesvg", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
            "slot_map": slot_map,
        })

        # Include a UI representation so execution caches.ui will record this
        # node's output in history. The 'ui' key will be collected by the
        # execution machinery and saved under history.outputs for the prompt.
        return {
            "ui": {"svg": (svg,)},
            "result": (svg,)
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveSVG": LF_SaveSVG,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveSVG": "Save SVG",
}
# endregion