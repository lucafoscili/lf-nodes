import json

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import get_comfy_dir, normalize_json_input, normalize_list_to_value, resolve_filepath

# region LF_SaveJSON
class LF_SaveJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_data": (Input.JSON, {
                    "tooltip": "JSON data to save."
                }),
                "filename_prefix": (Input.STRING, {
                    "default": '', 
                    "tooltip": "Path and filename for saving the JSON. Use slashes to set directories."
                }),
                "add_timestamp": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Add timestamp to the filename as a suffix."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
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
    RETURN_NAMES = ("json",)
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        json_data: dict = normalize_json_input(kwargs.get("json_data"))
        filename_prefix: str = normalize_list_to_value(kwargs.get("filename_prefix"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))

        output_file, _, _ = resolve_filepath(
            filename_prefix=filename_prefix,
            base_output_path=get_comfy_dir("output"),
            add_timestamp=add_timestamp,
            extension="json"
        )
 
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)
 
        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"check", "id": "root", "value": "JSON saved successfully!" }
        dataset: dict = { "nodes": [root] }
        nodes.append({ "description": output_file, "icon": "code", "id": output_file, "value": output_file })
 
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}savejson", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })
 
        return (json_data,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveJSON": LF_SaveJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveJSON": "Save JSON",
}
# endregion