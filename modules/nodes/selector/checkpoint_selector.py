import comfy.sd
import folder_paths
import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model_async
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import (
    build_is_changed_tuple,
    dataset_from_metadata,
    filter_list,
    is_none,
    LazyCache,
    normalize_list_to_value,
    register_cache,
    register_selector_list,
)
from ...utils.helpers.ui import prepare_model_dataset

# region LF_CheckpointSelector
class LF_CheckpointSelector:
    initial_list: list[str] = []
    _CACHE = LazyCache()
    _LAST_SELECTION: dict[str, str] = {}
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
    RETURN_TYPES = (initial_list, Input.STRING, Input.STRING, Input.IMAGE, Input.MODEL, Input.CLIP, Input.VAE)

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

        should_fetch_civitai = bool(get_civitai_info)
        event_name = f"{EVENT_PREFIX}checkpointselector"
        node_id = kwargs.get("node_id")

        callback = None
        if node_id and checkpoint:
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

                PromptServer.instance.send_sync(
                    event_name,
                    {
                        "node": node_id,
                        "datasets": [dataset_ready],
                        "hashes": [hash_event_ready],
                        "apiFlags": [fetch_flag_ready],
                        "paths": [model_path_ready or ""],
                    },
                )

            callback = _metadata_callback

        metadata = process_model_async("checkpoint", checkpoint, "checkpoints", on_complete=callback)
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

        PromptServer.instance.send_sync(
            event_name,
            {
                "node": node_id,
                "datasets": [dataset],
                "hashes": [hash_event],
                "apiFlags": [fetch_now],
                "paths": [path_event],
            },
        )

        return (
            checkpoint,
            metadata.get("model_name") or checkpoint,
            model_path,
            metadata.get("model_cover"),
            model,
            clip,
            vae,
        )

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
        ui_widget,
        node_id
    ):
        return build_is_changed_tuple(
            normalize_list_to_value(randomize),
            normalize_list_to_value(seed),
            normalize_list_to_value(filter),
            normalize_list_to_value(checkpoint),
            normalize_list_to_value(get_civitai_info),
        )
# endregion

# Register refresh handler so options update when ComfyUI refreshes node definitions
_CHECKPOINT_SELECTOR_LIST = register_selector_list(
    LF_CheckpointSelector,
    lambda: get_comfy_list("checkpoints"),
)

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CheckpointSelector": LF_CheckpointSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CheckpointSelector": "Checkpoint selector",
}
# endregion
