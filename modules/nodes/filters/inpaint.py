import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SAMPLERS, SCHEDULERS
from ...utils.filters.inpaint import apply_inpaint_filter_tensor
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_masks_for_images, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image
from ...utils.helpers.comfy import safe_send_sync

# region LF_Inpaint
class LF_Inpaint:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Base image."
                }),
                "mask": (Input.MASK, {
                    "tooltip": "Regions to inpaint (1=inpaint). Supports a single mask or a per-image mask list/batch.",
                }),
                "model": (Input.MODEL, {
                    "tooltip": "Diffusion model."
                }),
                "clip": (Input.CLIP, {
                    "tooltip": "CLIP text encoder."
                }),
                "vae": (Input.VAE, {
                    "tooltip": "VAE for encode/decode."
                }),
                "steps": (Input.INTEGER, {
                    "default": 16,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Number of diffusion steps to use."
                }),
                "denoise_percentage": (Input.FLOAT, {
                    "default": 40.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 1.0,
                    "tooltip": "Percentage of denoising to apply."
                }),
                "cfg": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.1,
                    "tooltip": "Classifier-free guidance scale."
                }),
            },
            "optional": {
                "positive_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "The prompt to guide the inpainting process."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "The prompt to discourage certain elements in the inpainting process."
                }),
                "use_conditioning": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Whether to use conditioning inputs."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Conditioning inputs to guide the inpainting process."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Conditioning inputs to discourage certain elements in the inpainting process."
                }),
                "upsample_target": (Input.INTEGER, {
                    "default": 1024,
                    "min": 0,
                    "max": 16384,
                    "tooltip": "If greater than 0, the image and mask will be upsampled to this size before inpainting."
                }),
                "sampler": (SAMPLERS, {
                    "default": "dpmpp_2m",
                    "tooltip": "The sampler to use for the diffusion process."
                }),
                "scheduler": (SCHEDULERS, {
                    "default": "karras",
                    "tooltip": "The scheduler to use for the diffusion process."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Image tensor with inpainting effect applied.",
        "List of image tensors with inpainting effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        node_id = kwargs.get("node_id")
        images = normalize_input_image(kwargs.get("image"))
        model = kwargs.get("model")
        clip = kwargs.get("clip")
        vae = kwargs.get("vae")

        if model is None or clip is None or vae is None:
            raise ValueError("Model, CLIP and VAE are required.")

        masks_list = normalize_masks_for_images(kwargs.get("mask"), len(images))
        mask_sequence = masks_list if len(masks_list) == len(images) else [masks_list[0]] * len(images)
        mask_iter = iter(mask_sequence)

        steps = int(normalize_list_to_value(kwargs.get("steps")))
        denoise_percentage = float(normalize_list_to_value(kwargs.get("denoise_percentage")))
        denoise = max(0.0, min(1.0, denoise_percentage / 100.0))

        settings = {
            "steps": steps,
            "denoise": denoise,
            "cfg": float(normalize_list_to_value(kwargs.get("cfg"))),
            "sampler": normalize_list_to_value(kwargs.get("sampler")) if kwargs.get("sampler") is not None else "dpmpp_2m",
            "scheduler": normalize_list_to_value(kwargs.get("scheduler")) if kwargs.get("scheduler") is not None else "karras",
            "positive_prompt": normalize_list_to_value(kwargs.get("positive_prompt") or ""),
            "negative_prompt": normalize_list_to_value(kwargs.get("negative_prompt") or ""),
            "use_conditioning": bool(normalize_list_to_value(kwargs.get("use_conditioning") or False)),
            "positive_conditioning": kwargs.get("positive_conditioning"),
            "negative_conditioning": kwargs.get("negative_conditioning"),
            "upsample_target": int(
                normalize_list_to_value(kwargs.get("upsample_target") if "upsample_target" in kwargs else 0)
            ),
        }

        def run_filter(
            t: torch.Tensor,
            *,
            settings=settings,
            model=model,
            clip=clip,
            vae=vae,
            mask_iter=mask_iter,
        ):
            mask_value = next(mask_iter)
            processed, _ = apply_inpaint_filter_tensor(
                image=t,
                mask=mask_value,
                model=model,
                clip=clip,
                vae=vae,
                settings=settings,
            )
            return processed

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=images,
            filter_function=run_filter,
            filter_args={},
            filename_prefix="inpaint",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        safe_send_sync(
            "inpaint",
            {
                "dataset": dataset,
            },
            node_id,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Inpaint": LF_Inpaint,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Inpaint": "Inpaint",
}
# endregion
