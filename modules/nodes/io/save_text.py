from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.logic import normalize_list_to_value

# region LF_SaveText
class LF_SaveText:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": (Input.STRING, {
                    "tooltip": "Plain text data to save (.txt)."
                }),
                "filename_prefix": (Input.STRING, {
                    "default": '', 
                    "tooltip": "Path and filename for saving the text. Use slashes to set directories."
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
    RETURN_NAMES = ("text",)
    RETURN_TYPES = ("STRING",)

    def on_exec(self, **kwargs: dict):
        text: dict = normalize_list_to_value(kwargs.get("text"))
        filename_prefix: str = normalize_list_to_value(kwargs.get("filename_prefix"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))
        add_counter: bool = normalize_list_to_value(kwargs.get("add_counter"))

        output_file, _, _ = resolve_filepath(
            filename_prefix=filename_prefix,
            base_output_path=get_comfy_dir("output"),
            add_timestamp=add_timestamp,
            extension="txt",
            add_counter=add_counter
        )
 
        with open(output_file, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
 
        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"check", "id": "root", "value": "TXT saved successfully!" }
        dataset: dict = { "nodes": [root] }
        nodes.append({ "description": output_file, "icon": "code", "id": output_file, "value": output_file })
 
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}savetext", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })
 
        return (text,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveText": LF_SaveText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveText": "Save text",
}
# endregion