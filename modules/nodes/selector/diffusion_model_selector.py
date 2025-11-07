import comfy.sd
import folder_paths
import random
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, WEIGHT_DTYPE_COMBO
from ...utils.helpers.api import process_model_async
from ...utils.helpers.comfy import get_comfy_list, safe_send_sync
from ...utils.helpers.logic import (
    build_is_changed_tuple,
    dataset_from_metadata,
    filter_list,
    is_none,
    LazyCache,
    make_model_cache_key,
    normalize_list_to_value,
    register_cache,
    register_selector_list,
)

_DIFFUSION_MODEL_CACHE = LazyCache()
register_cache(_DIFFUSION_MODEL_CACHE)

# region LF_DiffusionModelSelector
class LF_DiffusionModelSelector:
    initial_list: list[str] = []
    _LAST_SELECTION: dict[str, str] = {}

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
                "weight_dtype": (WEIGHT_DTYPE_COMBO, {
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
    OUTPUT_TOOLTIPS = (
        "Combo list of diffusion models.",
        "Selected diffusion model item as a string.",
        "Path to the selected diffusion model.",
        "Cover image of the selected diffusion model.",
        "Loaded diffusion model.",
    )
    RETURN_NAMES = ("combo", "string", "path", "image", "model")
    RETURN_TYPES = (initial_list, Input.STRING, Input.STRING, Input.IMAGE, Input.MODEL)

    def on_exec(self, **kwargs: dict):
        diffusion_model: str = normalize_list_to_value(kwargs.get("diffusion_model"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        weight_dtype: str = normalize_list_to_value(kwargs.get("weight_dtype", "default"))
        node_id = kwargs.get("node_id")

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
            except Exception:
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

        should_fetch_civitai = bool(get_civitai_info)
        event_name = f"{EVENT_PREFIX}diffusionmodelselector"

        callback = None
        if node_id and diffusion_model:
            def _metadata_callback(metadata_ready: dict) -> None:
                model_path_ready = metadata_ready.get("model_path")
                if not model_path_ready:
                    return
                if self._LAST_SELECTION.get(node_id) != model_path_ready:
                    return

                dataset_ready, hash_ready = dataset_from_metadata(metadata_ready)
                hash_event_ready = hash_ready if hash_ready and hash_ready != "Unknown" else ""
                fetch_flag_ready = should_fetch_civitai and bool(hash_event_ready)

                safe_send_sync(
                    "diffusionmodelselector",
                    {
                        "datasets": [dataset_ready],
                        "hashes": [hash_event_ready],
                        "apiFlags": [fetch_flag_ready],
                        "paths": [model_path_ready or ""],
                    },
                    node_id,
                )

            callback = _metadata_callback

        metadata = process_model_async("diffusion_model", diffusion_model, "unet", on_complete=callback)
        model_path = metadata.get("model_path")

        if node_id:
            if model_path:
                self._LAST_SELECTION[node_id] = model_path
            else:
                self._LAST_SELECTION.pop(node_id, None)

        dataset, hash_value = dataset_from_metadata(metadata)
        metadata_pending = bool(metadata.get("metadata_pending", False))
        hash_event = hash_value if hash_value and hash_value != "Unknown" else ""
        fetch_now = should_fetch_civitai and not metadata_pending and bool(hash_event)
        path_event = model_path or ""

        safe_send_sync(
            "diffusionmodelselector",
            {
                "datasets": [dataset],
                "hashes": [hash_event],
                "apiFlags": [fetch_now],
                "paths": [path_event],
            },
            node_id,
        )

        return (
            diffusion_model,
            metadata.get("model_name") or diffusion_model,
            model_path,
            metadata.get("model_cover"),
            model_obj,
        )

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
        weight_dtype,
        ui_widget,
        node_id
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

_DIFFUSION_MODEL_SELECTOR_LIST = register_selector_list(
    LF_DiffusionModelSelector,
    lambda: get_comfy_list("unet"),
)

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DiffusionModelSelector": LF_DiffusionModelSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DiffusionModelSelector": "Diffusion model selector",
}
# endregion
