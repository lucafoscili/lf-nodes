from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.logic import normalize_list_to_value

# region LF_SaveMarkdown
class LF_SaveMarkdown:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "markdown_text": (Input.STRING, {
                    "default": "", 
                    "multiline": True, 
                    "tooltip": "Markdown data to save."
                }),
                "filename_prefix": (Input.STRING, {
                    "default": '', 
                    "tooltip": "Path and filename for saving the Markdown. Use slashes to set directories."
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
    RETURN_NAMES = ("string",)
    RETURN_TYPES = ("STRING",)

    def on_exec(self, **kwargs: dict):
        markdown_text: str = normalize_list_to_value(kwargs.get("markdown_text"))
        filename_prefix: str = normalize_list_to_value(kwargs.get("filename_prefix"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))

        output_file, _, _ = resolve_filepath(
            filename_prefix=filename_prefix,
            base_output_path=get_comfy_dir("output"),
            add_timestamp=add_timestamp,
            extension="md"
        )

        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_text)

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"check", "id": "root", "value": "Markdown saved successfully!" }
        dataset: dict = { "nodes": [root] }
        nodes.append({ "description": output_file, "icon": "article", "id": output_file, "value": output_file })

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}savemarkdown", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (markdown_text,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveMarkdown": LF_SaveMarkdown,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveMarkdown": "Save Markdown",
}
# endregion