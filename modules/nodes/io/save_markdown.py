from pathlib import Path

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath, safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value

MARKDOWN_FILE_RECEIPT_SCHEMA = "lf.markdown_file.receipt.v1"

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
    OUTPUT_TOOLTIPS = (
        "Saved Markdown text.",
    )
    RETURN_NAMES = ("string",)
    RETURN_TYPES = (Input.STRING,)

    def on_exec(self, **kwargs: dict):
        markdown_text: str = normalize_list_to_value(kwargs.get("markdown_text"))
        filename_prefix: str = normalize_list_to_value(kwargs.get("filename_prefix"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))

        output_root = Path(get_comfy_dir("output")).resolve(strict=False)
        output_file, _, _ = resolve_filepath(
            filename_prefix=filename_prefix,
            base_output_path=str(output_root),
            add_timestamp=add_timestamp,
            extension="md"
        )

        output_path = Path(output_file).resolve(strict=False)
        try:
            relative_name = output_path.relative_to(output_root).as_posix()
        except ValueError as error:
            raise ValueError(
                "Resolved Markdown output path must remain inside ComfyUI's output directory."
            ) from error

        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_text)

        byte_length = output_path.stat().st_size
        receipt = {
            "schema": MARKDOWN_FILE_RECEIPT_SCHEMA,
            "file_name": relative_name,
            "storage_type": "output",
            "byte_length": byte_length,
        }

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"check", "id": "root", "value": "Markdown saved successfully!" }
        dataset: dict = { "nodes": [root] }
        nodes.append({
            "description": f"{byte_length} bytes",
            "icon": "article",
            "id": relative_name,
            "value": relative_name,
        })

        payload = {
            "dataset": dataset,
            "file_names": [relative_name],
            "receipt": receipt,
        }
        safe_send_sync("savemarkdown", payload, kwargs.get("node_id"))

        return {
            "ui": {"lf_output": [payload]},
            "result": (markdown_text,),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveMarkdown": LF_SaveMarkdown,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveMarkdown": "Save Markdown",
}
# endregion
