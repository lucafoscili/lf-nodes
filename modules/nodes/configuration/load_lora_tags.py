import re

from folder_paths import get_full_path
from pathlib import Path
from server import PromptServer

import comfy.sd
import comfy.utils

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import process_model
from ...utils.helpers.comfy import get_comfy_list, safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value
from ...utils.helpers.ui import  prepare_model_dataset

# region LF_LoadLoraTags
class LF_LoadLoraTags:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "get_civitai_info": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Attempts to retrieve more info about the models from CivitAI."
                }),
                "model": (Input.MODEL, {
                    "tooltip": "The main model to apply the LoRA to."
                }),
                "clip": (Input.CLIP, {
                    "tooltip": "The CLIP model to modify."
                }),
                "tags": (Input.STRING, {
                    "default": '',
                    "tooltip": "Text containing LoRA tags, e.g., <lora:example:1.0>"
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CARDS_WITH_CHIP, {
                    "default": ""
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Model with LoRA weights applied.",
        "CLIP model with LoRA weights applied."
    )
    RETURN_NAMES = ("model", "clip")
    RETURN_TYPES = (Input.MODEL, Input.CLIP)

    def on_exec(self, **kwargs: dict):
        def get_lora_weights(tag_content: str):
            name = tag_content[1]
            try:
                m_weight = float(tag_content[2]) if len(tag_content) > 2 else 1.0
                c_weight = float(tag_content[3]) if len(tag_content) > 3 else m_weight
            except ValueError:
                return None, None, None

            lora_files = get_comfy_list("loras")

            lora_name:str = None
            for lora_file in lora_files:
                if Path(lora_file).name.startswith(name) or lora_file.startswith(name):
                    lora_name = lora_file
                    break

            return lora_name, m_weight, c_weight
        def load_lora_file(lora_path: str):
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            return lora
        def add_chip(value: str):
            return { "icon": "x",
                     "description": "Failed to load this LoRA.",
                     "id": value,
                     "value": value }

        clip = normalize_list_to_value(kwargs.get("clip"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        model = normalize_list_to_value(kwargs.get("model"))
        tags: str = normalize_list_to_value(kwargs.get("tags"))

        regex = r"\<[0-9a-zA-Z\:\_\-\.\s\/\(\)\\\\]+\>"
        found_tags: list[str] = re.findall(regex, tags)

        api_flags: list[bool] = []
        nodes: list[dict] = []
        chip_dataset: dict =  { "nodes": nodes }
        datasets: list[dict] =  []
        hashes: list[str] = []
        lora_paths: list[str] = []
        lora_status: dict = {}

        if not found_tags:

            safe_send_sync("loadloratags", {
                "apiFlags": [False],
            }, kwargs.get("node_id"))

            return (model, clip)

        for tag in found_tags:
            tag_content = tag[1:-1].split(":")
            if tag_content[0] != 'lora' or len(tag_content) < 2:
                nodes.append(add_chip(tag_content))
                continue

            lora_name, m_weight, c_weight = get_lora_weights(tag_content)
            if not lora_name:
                nodes.append(add_chip(tag_content[1]))
                lora_status[tag_content[1]] = False
                continue

            if lora_name in lora_status:
                print(f"LoRA '{lora_name}' is already loaded, skipping.")
                continue

            lora_path = get_full_path("loras", lora_name)
            lora = load_lora_file(lora_path)

            model, clip = comfy.sd.load_lora_for_models(model, clip, lora, m_weight, c_weight)

            lora_status[lora_name] = True

            lora_data = process_model("lora", lora_name, "loras")
            name = lora_data["model_name"]
            hash = lora_data["model_hash"]
            path = lora_data["model_path"]
            base64 = lora_data["model_base64"]
            saved_info = lora_data["saved_info"]

            hashes.append(hash)
            lora_paths.append(path)

            if saved_info:
                datasets.append(saved_info)
                api_flags.append(False)
            else:
                datasets.append(prepare_model_dataset(name, hash, base64, path))
                api_flags.append(get_civitai_info)

        if not len(nodes):
            nodes.append({ "icon": "check",
                           "description": "Each LoRA has been loaded successfully!",
                           "id": "0",
                           "value": "LoRA loaded successfully!" })


        safe_send_sync("loadloratags", {
            "datasets": datasets,
            "hashes": hashes,
            "apiFlags": api_flags,
            "paths": lora_paths,
            "chip": chip_dataset
        }, kwargs.get("node_id"))

        return (model, clip)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadLoraTags": LF_LoadLoraTags,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadLoraTags": "Load LoRA tags",
}
# endregion
