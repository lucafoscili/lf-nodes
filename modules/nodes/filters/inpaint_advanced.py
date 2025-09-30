import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SAMPLERS, SCHEDULERS
from ...utils.filters.inpaint import apply_inpaint_filter_tensor
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_masks_for_images,  normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_InpaintAdvanced
class LF_InpaintAdvanced:
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
                    "default": 20,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Number of diffusion steps to use."
                }),
                "denoise": (Input.FLOAT, {
                    "default": 0.45,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Denoising strength. Higher values produce more changes."
                }),
                "cfg": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Classifier-Free Guidance scale. Higher values increase adherence to the prompt."
                }),
                "sampler": (SAMPLERS, {
                    "default": "dpmpp_2m",
                    "tooltip": "The sampler to use for the diffusion process."
                }),
                "scheduler": (SCHEDULERS, {
                    "default": "karras",
                    "tooltip": "The scheduler to use for the diffusion process."
                }),
                "seed": (Input.INTEGER, {
                    "default": -1,
                    "min": -1,
                    "max": 0xFFFFFFFFFFFFFFFF,
                    "tooltip": "Seed for the random number generator. Use -1 for a random seed."
                }),
            },
            "optional": {
                "positive_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Prompt to guide the inpainting process."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Prompt to discourage certain elements in the inpainting process."
                }),
                "use_conditioning": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Whether to use conditioning."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Conditioning inputs to guide the inpainting process."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Conditioning inputs to discourage certain elements in the inpainting process."
                }),
                "roi_auto": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Whether to automatically determine the ROI."
                }),
                "roi_padding": (Input.INTEGER, {
                    "default": 32,
                    "min": 0,
                    "max": 2048,
                    "tooltip": "Padding to apply to the ROI."
                }),
                "roi_align": (Input.INTEGER, {
                    "default": 8,
                    "min": 1,
                    "max": 128,
                    "tooltip": "Alignment for the ROI."
                }),
                "roi_align_auto": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Whether to automatically determine the ROI alignment."
                }),
                "roi_min_size": (Input.INTEGER, {
                    "default": 64,
                    "min": 1,
                    "max": 4096,
                    "tooltip": "Minimum size for the ROI."
                }),
                "dilate": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": 256,
                    "tooltip": "Amount to dilate the ROI."
                }),
                "feather": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": 256,
                    "tooltip": "Amount to feather the ROI."
                }),
                "upsample_target": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": 16384,
                    "tooltip": "Target size for upsampling."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("image", "image_list")
    OUTPUT_IS_LIST = (False, True)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        node_id = kwargs.get("node_id")
        images = normalize_input_image(kwargs.get("image"))
        model = kwargs.get("model")
        clip = kwargs.get("clip")
        vae = kwargs.get("vae")
        mask = kwargs.get("mask")

        if mask is None:
            raise ValueError("Mask is required for inpaint filter node.")
        if model is None or clip is None or vae is None:
            raise ValueError("Model, CLIP and VAE are required.")

        masks_list = normalize_masks_for_images(mask, len(images))
        mask_sequence = masks_list if len(masks_list) == len(images) else [masks_list[0]] * len(images)
        mask_iter = iter(mask_sequence)

        settings = {
            "steps": int(normalize_list_to_value(kwargs.get("steps"))),
            "denoise": float(normalize_list_to_value(kwargs.get("denoise"))),
            "cfg": float(normalize_list_to_value(kwargs.get("cfg"))),
            "sampler": normalize_list_to_value(kwargs.get("sampler")),
            "scheduler": normalize_list_to_value(kwargs.get("scheduler")),
            "seed": int(normalize_list_to_value(kwargs.get("seed"))),
            "positive_prompt": normalize_list_to_value(kwargs.get("positive_prompt") or ""),
            "negative_prompt": normalize_list_to_value(kwargs.get("negative_prompt") or ""),
            "use_conditioning": bool(normalize_list_to_value(kwargs.get("use_conditioning") or False)),
            "positive_conditioning": kwargs.get("positive_conditioning"),
            "negative_conditioning": kwargs.get("negative_conditioning"),
            "roi_auto": bool(normalize_list_to_value(kwargs.get("roi_auto") if "roi_auto" in kwargs else True)),
            "roi_padding": int(normalize_list_to_value(kwargs.get("roi_padding") if "roi_padding" in kwargs else 32)),
            "roi_align": int(normalize_list_to_value(kwargs.get("roi_align") if "roi_align" in kwargs else 8)),
            "roi_align_auto": bool(normalize_list_to_value(kwargs.get("roi_align_auto") if "roi_align_auto" in kwargs else False)),
            "roi_min_size": int(normalize_list_to_value(kwargs.get("roi_min_size") if "roi_min_size" in kwargs else 64)),
            "dilate": int(normalize_list_to_value(kwargs.get("dilate") if "dilate" in kwargs else 0)),
            "feather": int(normalize_list_to_value(kwargs.get("feather") if "feather" in kwargs else 0)),
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

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}inpaintadvanced",
            {
                "node": node_id,
                "dataset": dataset,
            },
        )

        batch_list, image_list = normalize_output_image(processed_images)
        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_InpaintAdvanced": LF_InpaintAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_InpaintAdvanced": "Inpaint (adv.)",
}
# endregion
