import fnmatch
import os

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value
from ...utils.helpers.ui import create_history_node

# region LF_LoadFileOnce
class LF_LoadFileOnce:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "dir": (Input.STRING, {
                    "tooltip": "Path to the directory containing the images to load."
                }),
                "subdir": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Indicates whether to also load images from subdirectories."
                }),
                "strip_ext": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Whether to remove file extensions from filenames."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Enables history, saving the execution value and date of the widget to prevent the same filename to be loaded twice."
                }),
            },
            "optional": {
                "filter": (Input.STRING, {
                    "default": "",
                    "tooltip": "This field can be used to filter file names. Supports wildcards (*)."
                }),
                "ui_widget": (Input.LF_HISTORY, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, False, True, True, True)
    OUTPUT_TOOLTIPS = (
        "File-blob of the loaded file.",
        "Content of the loaded file as string.",
        "Name of the loaded file.",
        "List of file-blobs of the loaded files.",
        "List of contents of the loaded files as strings.",
        "List of names of the loaded files."
    )
    RETURN_NAMES = ("file_blob", "file_content", "name", "file_blob_list", "file_content_list", "name_list")
    RETURN_TYPES = (Input.FILE_BLOB, Input.STRING, Input.STRING, Input.FILE_BLOB, Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        dir: str = normalize_list_to_value(kwargs.get("dir"))
        subdir: bool = normalize_list_to_value(kwargs.get("subdir"))
        strip_ext: bool = normalize_list_to_value(kwargs.get("strip_ext"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        filter: str = normalize_list_to_value(kwargs.get("filter")).strip()
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        nodes: list[dict] = ui_widget.get("nodes", [])
        previous_files: dict = { node['value'] for node in nodes } if nodes else set()

        data, file_name, text = None, None, None

        for root, dirs, filenames in os.walk(dir):
            if not subdir:
                dirs[:] = []

            if filter and os.sep in filter and filter not in os.path.join(root, ''):
                continue

            for filename in filenames:
                if filter and os.sep not in filter:
                    if not fnmatch.fnmatch(filename, filter):
                        continue

                file_name_stripped = os.path.splitext(filename)[0] if strip_ext else filename
                if file_name_stripped in previous_files:
                    continue

                file_path = os.path.join(root, filename)
                with open(file_path, "rb") as f:
                    data = f.read()
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = ""

                file_name = file_name_stripped

                if enable_history:
                    create_history_node(file_name_stripped, nodes)
                break

        dataset: dict  = { "nodes": nodes }

        safe_send_sync("loadfileonce", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (data, text, file_name, [data], [text], [file_name])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadFileOnce": LF_LoadFileOnce,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadFileOnce": "Load file from disk once",
}
# endregion
