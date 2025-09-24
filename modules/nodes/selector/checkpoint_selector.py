import comfy.sd
import folder_paths
import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import build_is_changed_tuple, filter_list, is_none, LazyCache, normalize_list_to_value, register_cache
from ...utils.helpers.ui import prepare_model_dataset

# region LF_CheckpointSelector
class LF_CheckpointSelector:
    initial_list = get_comfy_list("checkpoints")
    _CACHE = LazyCache()
    register_cache(_CACHE)

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "checkpoint": (["None"] + self.initial_list, {
                    "default": "None", 
                    "tooltip": "Checkpoint used to generate the image."
                }),
                "get_civitai_info": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Attempts to retrieve more info about the model from CivitAI."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Selects a checkpoint randomly from your checkpoints directory."
                }),
                "filter": (Input.STRING, {
                    "default": "", 
                    "tooltip": "When randomization is active, this field can be used to filter checkpoint file names. Supports wildcards (*)"
                }),
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "min": 0, 
                    "max": INT_MAX, 
                    "tooltip": "Seed value for when randomization is active."
                }),
            },
            "optional": {
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
    RETURN_NAMES = ("combo", "string", "path", "image", "model", "clip", "vae")
    RETURN_TYPES = (initial_list, "STRING", "STRING", "IMAGE", "MODEL", "CLIP", "VAE")

    def on_exec(self, **kwargs: dict):
        checkpoint: str = normalize_list_to_value(kwargs.get("checkpoint"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))

        if is_none(checkpoint):
            checkpoint = None 
        
        checkpoints = get_comfy_list("checkpoints")

        if randomize:
            if filter:
                checkpoints = filter_list(filter, checkpoints)
                if not checkpoints:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            checkpoint = random.choice(checkpoints)

        model = None
        clip = None
        vae = None
        
        if checkpoint:
            ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", checkpoint)
            key = ("ckpt", ckpt_path)
            out = self._CACHE.get_or_set(
                key,
                lambda: comfy.sd.load_checkpoint_guess_config(
                    ckpt_path,
                    output_vae=True,
                    output_clip=True,
                    embedding_directory=folder_paths.get_folder_paths("embeddings"),
                ),
            )
            model, clip, vae = out[:3]

        checkpoint_data = process_model("checkpoint", checkpoint, "checkpoints")
        model_name = checkpoint_data["model_name"]
        model_hash = checkpoint_data["model_hash"]
        model_path = checkpoint_data["model_path"]
        model_base64 = checkpoint_data["model_base64"]
        model_cover = checkpoint_data["model_cover"]
        saved_info = checkpoint_data["saved_info"]

        if saved_info:
            dataset = saved_info
            get_civitai_info = False
        else:
            dataset = prepare_model_dataset(model_name, model_hash, model_base64, model_path)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}checkpointselector", {
            "node": kwargs.get("node_id"),
            "datasets": [dataset],
            "hashes": [model_hash],
            "apiFlags": [get_civitai_info],
            "paths": [model_path],
        })

        return (checkpoint, model_name, model_path, model_cover, model, clip, vae)
    
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True

    @classmethod
    def IS_CHANGED(
        cls,
        checkpoint,
        get_civitai_info,
        randomize,
        filter,
        seed,
        ui_widget
    ):
        return build_is_changed_tuple(
            normalize_list_to_value(randomize),
            normalize_list_to_value(seed),
            normalize_list_to_value(filter),
            normalize_list_to_value(checkpoint),
            normalize_list_to_value(get_civitai_info),
        )
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CheckpointSelector": LF_CheckpointSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CheckpointSelector": "Checkpoint selector",
}
# endregion