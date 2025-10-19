import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SAMPLERS, SCHEDULERS
from ...utils.helpers.editing import EditingSession
from ...utils.helpers.logic import normalize_conditioning, normalize_input_image, normalize_list_to_value, normalize_output_image
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
                "sampler": (SAMPLERS, {
                    "tooltip": "Optional sampler reused by inpaint edits.",
                    "default": "dpmpp_2m"
                }),
                "scheduler": (SCHEDULERS, {
                    "tooltip": "Optional scheduler reused by inpaint edits.",
                    "default": "normal"
                }),
                "cfg": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 30.0,
                    "step": 0.1,
                    "tooltip": "CFG scale used as the starting value for inpaint edits."
                }),
                "positive_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional positive prompt used to pre-fill the inpaint editor."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional negative prompt used to pre-fill the inpaint editor."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional positive conditioning to reuse during inpaint edits."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional negative conditioning to reuse during inpaint edits."
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
    OUTPUT_IS_LIST = (False, True, False, True)
    OUTPUT_TOOLTIPS = (
        "Edited image tensor.",
        "List of edited image tensors.",
        "Original image tensor.",
        "List of original image tensors."
    )
    RETURN_NAMES = ("image", "image_list", "orig_image", "orig_image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs):
        self._temp_cache.cleanup()

        session = EditingSession(node_id=kwargs.get("node_id"), temp_cache=self._temp_cache)

        model_value = normalize_list_to_value(kwargs.get("model"))
        clip_value = normalize_list_to_value(kwargs.get("clip"))
        vae_value = normalize_list_to_value(kwargs.get("vae"))
        sampler_value = normalize_list_to_value(kwargs.get("sampler"))
        scheduler_value = normalize_list_to_value(kwargs.get("scheduler"))

        cfg_raw = normalize_list_to_value(kwargs.get("cfg"))
        try:
            cfg_value = float(cfg_raw) if cfg_raw is not None else None
        except (TypeError, ValueError):
            cfg_value = None

        seed_raw = normalize_list_to_value(kwargs.get("seed"))
        try:
            seed_value = int(seed_raw) if seed_raw not in (None, "") else None
        except (TypeError, ValueError):
            seed_value = None

        positive_prompt_raw = normalize_list_to_value(kwargs.get("positive_prompt"))
        positive_prompt_value = str(positive_prompt_raw) if positive_prompt_raw not in (None, "") else ""

        negative_prompt_raw = normalize_list_to_value(kwargs.get("negative_prompt"))
        negative_prompt_value = str(negative_prompt_raw) if negative_prompt_raw not in (None, "") else ""

        positive_conditioning_value = normalize_conditioning(kwargs.get("positive_conditioning"))
        negative_conditioning_value = normalize_conditioning(kwargs.get("negative_conditioning"))

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        dataset = session.build_dataset(image, filename_prefix="edit_breakpoint")

        inpaint_defaults: dict[str, object] = {}
        if cfg_value is not None:
            inpaint_defaults["cfg"] = cfg_value
        if seed_value is not None and seed_value >= 0:
            inpaint_defaults["seed"] = seed_value
        if positive_prompt_value:
            inpaint_defaults["positive_prompt"] = positive_prompt_value
        if negative_prompt_value:
            inpaint_defaults["negative_prompt"] = negative_prompt_value

        if inpaint_defaults:
            dataset.setdefault("defaults", {})["inpaint"] = inpaint_defaults

        session.register_context(
            dataset,
            model=model_value,
            clip=clip_value,
            vae=vae_value,
            sampler=sampler_value,
            scheduler=scheduler_value,
            cfg=cfg_value,
            seed=seed_value,
            positive_prompt=positive_prompt_value or None,
            negative_prompt=negative_prompt_value or None,
            positive_conditioning=positive_conditioning_value,
            negative_conditioning=negative_conditioning_value,
        )

        try:
            PromptServer.instance.send_sync(
                f"{EVENT_PREFIX}imageseditingbreakpoint",
                {
                    "node": kwargs.get("node_id"),
                    "value": dataset.get("context_id"),
                },
            )
            dataset = session.wait_for_completion(dataset)
        except Exception:
            session.cleanup(dataset)
            raise

        batch_list, image_list = normalize_output_image(image)
        results = session.collect_results(dataset)
        edited_batch_list, edited_image_list = results.batch_list, results.image_list

        return (edited_batch_list[0], edited_image_list, batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImagesEditingBreakpoint": LF_ImagesEditingBreakpoint,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImagesEditingBreakpoint": "Images editing breakpoint",
}
# endregion
