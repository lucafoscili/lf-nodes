import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import (
    filter_list,
    is_none,
    normalize_list_to_value,
    register_selector_list,
)
from ...utils.helpers.ui import prepare_model_dataset

# region LF_LoraSelector
class LF_LoraSelector:
    initial_list: list[str] = []
        
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "lora": (["None"] + self.initial_list, {
                    "default": "None", 
                    "tooltip": "Lora model to use."
                }),
                "get_civitai_info": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Attempts to retrieve more info about the model from CivitAI."
                }),
                "weight": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": -3.0, 
                    "max": 3.0, 
                    "tooltip": "Lora weight."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Selects a Lora randomly from your loras directory."
                }),
                "filter": (Input.STRING, {
                    "default": "", 
                    "tooltip": "When randomization is active, this field can be used to filter Lora file names. Supports wildcards (*)."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "min": 0, 
                    "max": INT_MAX, 
                    "tooltip": "Seed value for when randomization is active."
                }),
            },
            "optional": {
                "lora_stack": (Input.STRING, {
                    "default": "", 
                    "forceInput": True, 
                    "tooltip": "Optional string usable to concatenate subsequent selector nodes."
                }),
                "ui_widget": (Input.LF_CARD, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("lora", "lora_tag", "lora_name", "model_path", "model_cover")
    RETURN_TYPES = (initial_list, "STRING", "STRING", "STRING", "IMAGE")

    def on_exec(self, **kwargs: dict):
        lora: str = normalize_list_to_value(kwargs.get("lora"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        weight: float = normalize_list_to_value(kwargs.get("weight"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        lora_stack: str = normalize_list_to_value(kwargs.get("lora_stack", ""))

        if is_none(lora):
            lora = None

        passthrough = bool(not lora and not randomize)

        if passthrough:

            PromptServer.instance.send_sync(f"{EVENT_PREFIX}loraselector", {
                "node": kwargs.get("node_id"),
                "apiFlags": [False],
            })

            return (None, lora_stack, "", "", None)
        
        loras = get_comfy_list("loras")

        if randomize:
            if filter:
                loras = filter_list(filter, loras)
                if not loras:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            lora = random.choice(loras)

        lora_data = process_model("lora", lora, "loras")
        model_name = lora_data["model_name"]
        model_hash = lora_data["model_hash"]
        model_path = lora_data["model_path"]
        model_base64 = lora_data["model_base64"]
        model_cover = lora_data["model_cover"]
        saved_info = lora_data["saved_info"]

        lora_tag = f"<lora:{model_name}:{weight}>"

        if saved_info:
            dataset = saved_info
            get_civitai_info = False
        else:
            dataset = prepare_model_dataset(model_name, model_hash, model_base64, model_path)

        if lora_stack:
            lora_tag = f"{lora_tag}, {lora_stack}"

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loraselector", {
            "node": kwargs.get("node_id"),
            "datasets": [dataset],
            "hashes": [model_hash],
            "apiFlags": [get_civitai_info],
            "paths": [model_path],
        })

        return (lora, lora_tag, model_name, model_path, model_cover)
    
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True
# endregion

_LORA_SELECTOR_LIST = register_selector_list(
    LF_LoraSelector,
    lambda: get_comfy_list("loras"),
)

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoraSelector": LF_LoraSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoraSelector": "LoRA selector",
}
# endregion