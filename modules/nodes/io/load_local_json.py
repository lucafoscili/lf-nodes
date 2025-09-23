import json
import requests

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

# region LF_LoadLocalJSON
class LF_LoadLocalJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "url": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The local URL where the JSON file is stored (i.e.: file://C:/myjson.json)."
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
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        url: str = normalize_list_to_value(kwargs.get("url"))

        if not url.startswith("file://"):
            url = f"file://{url}"
        
        file_path = requests.utils.unquote(url[7:])
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
 
        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"check", "id": "root", "value": "JSON loaded successfully!" }
        dataset: dict = { "nodes": [root] }
        nodes.append({ "description": url, "icon": "json", "id": url, "value": url })
 
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}savejson", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (data,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadLocalJSON": LF_LoadLocalJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadLocalJSON": "Load JSON from disk",
}
# endregion