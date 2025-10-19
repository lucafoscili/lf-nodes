import os
import re

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value
from ...utils.helpers.ui import create_history_node

# region LF_RegionExtractor
class LF_RegionExtractor:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "dir": (Input.STRING, {
                    "tooltip": "Path to the directory or file containing the Python files."
                }),
                "subdir": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Whether to load Python files from subdirectories as well."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Tracks extracted regions to avoid reprocessing."
                }),
                "extension": (Input.STRING, {
                    "default": "py",
                    "tooltip": "Extension of the files that will be read."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Extracted code regions.",
        "List of all extracted code regions.",
    )
    RETURN_NAMES = ("regions", "regions_list")
    RETURN_TYPES = (Input.JSON, Input.JSON)

    def on_exec(self, **kwargs: dict):
        def find_missing_references(code):
            """
            Identify constants and helper functions that are used but not defined in the code region.
            """
            # Patterns for constants (uppercase words) and function calls
            constant_pattern = r'\b([A-Z_][A-Z0-9_]*)\b'
            function_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('

            # All defined names within the region
            defined_names = set(re.findall(r'\bdef ([a-zA-Z_][a-zA-Z0-9_]*)\b|\b([A-Z_][A-Z0-9_]*)\b\s*=', code))
            defined_functions = {name[0] for name in defined_names if name[0]}
            defined_constants = {name[1] for name in defined_names if name[1]}

            # Find all constants and functions used in the code
            used_constants = set(re.findall(constant_pattern, code))
            used_functions = set(re.findall(function_pattern, code))

            # Missing constants and functions
            missing_constants = list(used_constants - defined_constants)
            missing_functions = list(used_functions - defined_functions)

            return missing_constants, missing_functions

        dir_path: str = normalize_list_to_value(kwargs.get("dir"))
        subdir: bool = normalize_list_to_value(kwargs.get("subdir"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        extension: str = normalize_list_to_value(kwargs.get("extension"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        if not extension.startswith("."):
            extension = f".{extension}"

        files: list[str] = []
        if os.path.isfile(dir_path):
            # 'dir' is actually a file
            if dir_path.endswith(extension):
                files.append(dir_path)
            else:
                # The file does not have the correct extension
                print(f"The file {dir_path} does not have the '{extension}' extension.")
                return ({}, [])
        elif os.path.isdir(dir_path):
            # 'dir' is a directory
            for root, _, f in os.walk(dir_path):
                if not subdir and root != dir_path:
                    continue
                files.extend([os.path.join(root, file) for file in f if file.endswith(extension)])
        else:
            print(f"The path {dir_path} is neither a file nor a directory.")
            return ({}, [])

        regions_list: list[dict] = []
        nodes: list[dict] = ui_widget.get("nodes", [])

        for file_path in files:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()

                if enable_history and ui_widget.get(file_path):
                    continue

                pattern = r"# region (.+?)\n(.*?)# endregion"
                matches = re.findall(pattern, code, re.DOTALL)

                for match in matches:
                    name = match[0].strip()
                    code_region = match[1].strip()

                    constants, helper_functions = find_missing_references(code_region)

                    if enable_history:
                        create_history_node(name, nodes)

                    regions_list.append({
                        "file": file_path,
                        "name": name,
                        "code": code_region,
                        "constants": constants,
                        "helperFunctions": helper_functions
                    })

        dataset: dict = {"nodes": nodes}

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}regionextractor", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (regions_list, regions_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_RegionExtractor": LF_RegionExtractor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_RegionExtractor": "Extract region from sources",
}
# endregion
