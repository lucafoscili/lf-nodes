import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.editing import (
    EditingSession,
    apply_editor_config_to_dataset,
    build_editor_config_from_dataset,
)
from ...utils.helpers.logic import (
    normalize_conditioning,
    normalize_input_image,
    normalize_json_input,
    normalize_list_to_value,
    normalize_output_image,
)
from ...utils.helpers.temp_cache import TempFileCache

# region LF_ImagesEditingBreakpoint
class LF_ImagesEditingBreakpoint:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Batch of images."
                }),
            },
            "optional": {
                "model": (Input.MODEL, {
                    "tooltip": "Optional diffusion model reused by inpaint edits."
                }),
                "clip": (Input.CLIP, {
                    "tooltip": "Optional CLIP encoder reused by inpaint edits."
                }),
                "vae": (Input.VAE, {
                    "tooltip": "Optional VAE reused by inpaint edits."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional positive conditioning to reuse during inpaint edits."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional negative conditioning to reuse during inpaint edits."
                }),
                "wd14_tagger": (Input.TAGGER, {
                    "tooltip": "Optional WD14 tagger (HF or ONNX) reused by inpaint edits."
                }),
                "config": (Input.JSON, {
                    "tooltip": "Optional image editor configuration JSON (navigation/defaults/selection)."
                }),
                "ui_widget": (Input.LF_IMAGE_EDITOR, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True, False)
    OUTPUT_TOOLTIPS = (
        "Edited image tensor.",
        "List of edited image tensors.",
        "Original image tensor.",
        "List of original image tensors.",
        "Image editor configuration JSON (navigation/defaults/selection).",
    )
    RETURN_NAMES = ("image", "image_list", "orig_image", "orig_image_list", "config")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.JSON)

    def on_exec(self, **kwargs):
        self._temp_cache.cleanup()

        node_id = kwargs.get("node_id")
        session = EditingSession(node_id=node_id, temp_cache=self._temp_cache)

        model_value = normalize_list_to_value(kwargs.get("model"))
        clip_value = normalize_list_to_value(kwargs.get("clip"))
        vae_value = normalize_list_to_value(kwargs.get("vae"))

        positive_conditioning_value = normalize_conditioning(kwargs.get("positive_conditioning"))
        negative_conditioning_value = normalize_conditioning(kwargs.get("negative_conditioning"))

        wd14_tagger_value = normalize_list_to_value(kwargs.get("wd14_tagger"))

        config_raw = kwargs.get("config")
        try:
            config_value = normalize_json_input(config_raw) if config_raw is not None else None
        except TypeError:
            config_value = None

        ui_state_raw = kwargs.get("ui_widget")
        try:
            ui_state_value = normalize_json_input(ui_state_raw) if ui_state_raw is not None else None
        except TypeError:
            ui_state_value = None

        if config_value is None and isinstance(ui_state_value, dict):
            config_value = build_editor_config_from_dataset(ui_state_value)

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        dataset = session.build_dataset(image, filename_prefix="edit_breakpoint")

        if isinstance(config_value, dict):
            apply_editor_config_to_dataset(dataset, config_value)

        session.register_context(
            dataset,
            model=model_value,
            clip=clip_value,
            vae=vae_value,
            positive_conditioning=positive_conditioning_value,
            negative_conditioning=negative_conditioning_value,
            wd14_tagger=wd14_tagger_value,
            node_event="imageseditingbreakpoint",
        )

        try:
            safe_send_sync(
                "imageseditingbreakpoint",
                {
                    "value": dataset.get("context_id"),
                },
                node_id,
            )
            dataset = session.wait_for_completion(dataset)
        except Exception:
            session.cleanup(dataset)
            raise

        batch_list, image_list = normalize_output_image(image)
        results = session.collect_results(dataset)
        edited_batch_list, edited_image_list = results.batch_list, results.image_list

        config_out = build_editor_config_from_dataset(dataset)

        return (edited_batch_list[0], edited_image_list, batch_list[0], image_list, config_out)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImagesEditingBreakpoint": LF_ImagesEditingBreakpoint,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImagesEditingBreakpoint": "Images editing breakpoint",
}
# endregion
