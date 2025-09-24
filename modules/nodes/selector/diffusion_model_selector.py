import comfy.sd
import folder_paths
import random
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import build_is_changed_tuple, filter_list, is_none, LazyCache, make_model_cache_key, normalize_list_to_value
from ...utils.helpers.ui import prepare_model_dataset

_DIFFUSION_MODEL_CACHE = LazyCache()

# region LF_DiffusionModelSelector
class LF_DiffusionModelSelector:
    initial_list = get_comfy_list("unet")

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "diffusion_model": (["None"] + self.initial_list, {
                    "default": "None", 
                    "tooltip": "Diffusion model used to generate the image ('unet' folder)."
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
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"], {
                    "default": "default",
                    "tooltip": "Weight data type for the diffusion model. 'default' will use the default data type for the model, while the others will force a specific data type."
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
    RETURN_NAMES = ("combo", "string", "path", "image", "model")
    RETURN_TYPES = (initial_list, "STRING", "STRING", "IMAGE", "MODEL")

    def on_exec(self, **kwargs: dict):
        diffusion_model: str = normalize_list_to_value(kwargs.get("diffusion_model"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        weight_dtype: str = normalize_list_to_value(kwargs.get("weight_dtype", "default"))

        if is_none(diffusion_model):
            diffusion_model = None 
        
        models = get_comfy_list("unet")

        if randomize:
            if filter:
                models = filter_list(filter, models)
                if not models:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            diffusion_model = random.choice(models)

        model_obj = None
        if diffusion_model:
            
            model_options = {}
            if weight_dtype == "fp8_e4m3fn":
                model_options["dtype"] = torch.float8_e4m3fn
            elif weight_dtype == "fp8_e4m3fn_fast":
                model_options["dtype"] = torch.float8_e4m3fn
                model_options["fp8_optimizations"] = True
            elif weight_dtype == "fp8_e5m2":
                model_options["dtype"] = torch.float8_e5m2

            try:
                unet_path = folder_paths.get_full_path_or_raise("diffusion_models", diffusion_model)
                key = make_model_cache_key(
                    unet_path,
                    dtype=model_options.get("dtype"),
                    fp8_opt=model_options.get("fp8_optimizations", False),
                )
                model_obj = _DIFFUSION_MODEL_CACHE.get_or_set(
                    key, lambda: comfy.sd.load_diffusion_model(unet_path, model_options=model_options)
                )
            except:
                try:
                    unet_path = folder_paths.get_full_path_or_raise("unet", diffusion_model)
                    key = make_model_cache_key(
                        unet_path,
                        dtype=model_options.get("dtype"),
                        fp8_opt=model_options.get("fp8_optimizations", False),
                    )
                    model_obj = _DIFFUSION_MODEL_CACHE.get_or_set(
                        key, lambda: comfy.sd.load_diffusion_model(unet_path, model_options=model_options)
                    )
                except Exception as e:
                    print(f"Failed to load diffusion model {diffusion_model}: {e}")
                    model_obj = None

        checkpoint_data = process_model("diffusion_model", diffusion_model, "unet")
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

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}diffusionmodelselector", {
            "node": kwargs.get("node_id"),
            "datasets": [dataset],
            "hashes": [model_hash],
            "apiFlags": [get_civitai_info],
            "paths": [model_path],
        })

        return (diffusion_model, model_name, model_path, model_cover, model_obj)
    
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True

    @classmethod
    def IS_CHANGED(
        cls,
        diffusion_model,
        get_civitai_info,
        randomize,
        filter,
        seed,
        weight_dtype
    ):
        return build_is_changed_tuple(
            normalize_list_to_value(randomize),
            normalize_list_to_value(seed),
            normalize_list_to_value(filter),
            normalize_list_to_value(diffusion_model),
            normalize_list_to_value(weight_dtype),
            normalize_list_to_value(get_civitai_info),
        )
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DiffusionModelSelector": LF_DiffusionModelSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DiffusionModelSelector": "Diffusion model selector",
}
# endregion