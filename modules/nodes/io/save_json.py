import json
from pathlib import Path

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath, safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value

JSON_FILE_RECEIPT_SCHEMA = "lf.json_file.receipt.v1"

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
    OUTPUT_TOOLTIPS = (
        "Saved JSON file path.",
    )
    RETURN_NAMES = ("json",)
    RETURN_TYPES = (Input.JSON,)

    def on_exec(self, **kwargs: dict):
        json_data: dict = normalize_json_input(kwargs.get("json_data"))
        filename_prefix: str = normalize_list_to_value(kwargs.get("filename_prefix"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))

        output_root = Path(get_comfy_dir("output")).resolve(strict=False)
        output_file, _, _ = resolve_filepath(
            filename_prefix=filename_prefix,
            base_output_path=str(output_root),
            add_timestamp=add_timestamp,
            extension="json"
        )

        output_path = Path(output_file).resolve(strict=False)
        try:
            relative_path = output_path.relative_to(output_root)
        except ValueError as error:
            raise ValueError(
                "Resolved JSON output path must remain inside ComfyUI's output directory."
            ) from error

        relative_name = relative_path.as_posix()

        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        byte_length = output_path.stat().st_size
        receipt = {
            "schema": JSON_FILE_RECEIPT_SCHEMA,
            "file_name": relative_name,
            "storage_type": "output",
            "byte_length": byte_length,
        }

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"check", "id": "root", "value": "JSON saved successfully!" }
        dataset: dict = { "nodes": [root] }
        nodes.append({
            "description": f"{byte_length} bytes",
            "icon": "code",
            "id": relative_name,
            "value": relative_name,
        })

        safe_send_sync("savejson", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return {
            "ui": {
                "lf_output": [{
                    "dataset": dataset,
                    "file_names": [relative_name],
                    "receipt": receipt,
                }],
            },
            "result": (json_data,),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveJSON": LF_SaveJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveJSON": "Save JSON",
}
# endregion
