import random

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model_async
from ...utils.helpers.comfy import get_comfy_list, safe_send_sync
from ...utils.helpers.logic import (
    dataset_from_metadata,
    filter_list,
    is_none,
    normalize_list_to_value,
    register_selector_list,
)

# region LF_LoraSelector
class LF_LoraSelector:
    initial_list: list[str] = []
    _LAST_SELECTION: dict[str, str] = {}

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
    OUTPUT_TOOLTIPS = (
        "Combo list of the LoRAs.",
        "Selected LoRA item as a combo.",
        "Selected LoRA item as a string.",
        "File path of the LoRA.",
        "Image of the LoRA (when available).",
        "LoRA model.",
    )
    RETURN_NAMES = ("lora", "lora_tag", "lora_name", "model_path", "model_cover")
    RETURN_TYPES = (initial_list, Input.STRING, Input.STRING, Input.STRING, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        lora: str = normalize_list_to_value(kwargs.get("lora"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        weight: float = normalize_list_to_value(kwargs.get("weight"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        lora_stack: str = normalize_list_to_value(kwargs.get("lora_stack", ""))
        node_id = kwargs.get("node_id")

        if is_none(lora):
            lora = None

        passthrough = bool(not lora and not randomize)

        if passthrough:

            safe_send_sync("loraselector", {
                "apiFlags": [False],
            }, node_id)

            if node_id:
                self._LAST_SELECTION.pop(node_id, None)

            return (None, lora_stack, "", "", None)

        loras = get_comfy_list("loras")

        if randomize:
            if filter:
                loras = filter_list(filter, loras)
                if not loras:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            lora = random.choice(loras)

        should_fetch_civitai = bool(get_civitai_info)

        callback = None
        if node_id and lora:
            def _metadata_callback(metadata_ready: dict) -> None:
                model_path_ready = metadata_ready.get("model_path")
                if not model_path_ready:
                    return
                if self._LAST_SELECTION.get(node_id) != model_path_ready:
                    return

                dataset_ready, hash_ready = dataset_from_metadata(metadata_ready)
                hash_event_ready = hash_ready if hash_ready and hash_ready != "Unknown" else ""
                fetch_flag_ready = (
                    should_fetch_civitai
                    and not metadata_ready.get("saved_info")
                    and bool(hash_event_ready)
                )

                safe_send_sync(
                    "loraselector",
                    {
                        "datasets": [dataset_ready],
                        "hashes": [hash_event_ready],
                        "apiFlags": [fetch_flag_ready],
                        "paths": [model_path_ready or ""],
                    },
                    node_id,
                )

            callback = _metadata_callback

        metadata = process_model_async("lora", lora, "loras", on_complete=callback)
        model_path = metadata.get("model_path")

        if node_id:
            if model_path:
                self._LAST_SELECTION[node_id] = model_path
            else:
                self._LAST_SELECTION.pop(node_id, None)

        dataset, hash_value = dataset_from_metadata(metadata)
        if metadata.get("saved_info"):
            should_fetch_civitai = False

        metadata_pending = bool(metadata.get("metadata_pending", False))
        hash_event = hash_value if hash_value and hash_value != "Unknown" else ""
        fetch_now = (
            should_fetch_civitai
            and not metadata.get("saved_info")
            and not metadata_pending
            and bool(hash_event)
        )
        path_event = model_path or ""

        model_name = metadata.get("model_name") or lora
        lora_tag = f"<lora:{model_name}:{weight}>"
        if lora_stack:
            lora_tag = f"{lora_tag}, {lora_stack}"

        safe_send_sync(
            "loraselector",
            {
                "datasets": [dataset],
                "hashes": [hash_event],
                "apiFlags": [fetch_now],
                "paths": [path_event],
            },
            node_id,
        )

        return (lora, lora_tag, model_name, model_path, metadata.get("model_cover"))

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
