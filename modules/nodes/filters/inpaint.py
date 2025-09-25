import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SAMPLERS, SCHEDULERS
from ...utils.filters.inpaint import apply_inpaint_filter_tensor
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.torch import process_and_save_image

# region LF_Inpaint
class LF_Inpaint:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Base image."}),
                "mask": ("MASK", {"tooltip": "Regions to inpaint (1=inpaint). Supports a single mask or a per-image mask list/batch."}),
                "model": ("MODEL", {"tooltip": "Diffusion model."}),
                "clip": ("CLIP", {"tooltip": "CLIP text encoder."}),
                "vae": ("VAE", {"tooltip": "VAE for encode/decode."}),
                "steps": (Input.INTEGER, {"default": 20, "min": 1, "max": 10000}),
                "denoise": (Input.FLOAT, {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "cfg": (Input.FLOAT, {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.01}),
                "sampler": (SAMPLERS, {}),
                "scheduler": (SCHEDULERS, {}),
                "seed": (Input.INTEGER, {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "positive_prompt": (Input.STRING, {"default": ""}),
                "negative_prompt": (Input.STRING, {"default": ""}),
                "use_conditioning": (Input.BOOLEAN, {"default": False}),
                "positive_conditioning": (Input.CONDITIONING, {}),
                "negative_conditioning": (Input.CONDITIONING, {}),
                "roi_auto": (Input.BOOLEAN, {"default": True}),
                "roi_padding": (Input.INTEGER, {"default": 32, "min": 0, "max": 2048}),
                "roi_align": (Input.INTEGER, {"default": 8, "min": 1, "max": 128}),
                "roi_align_auto": (Input.BOOLEAN, {"default": False}),
                "roi_min_size": (Input.INTEGER, {"default": 64, "min": 1, "max": 4096}),
                "dilate": (Input.INTEGER, {"default": 0, "min": 0, "max": 256}),
                "feather": (Input.INTEGER, {"default": 0, "min": 0, "max": 256}),
                "upsample_target": (Input.INTEGER, {"default": 0, "min": 0, "max": 16384}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("image", "image_list")
    OUTPUT_IS_LIST = (False, True)

    def on_exec(self, **kwargs: dict):
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
            "upsample_target": int(normalize_list_to_value(kwargs.get("upsample_target") if "upsample_target" in kwargs else 0)),
        }

        masks_list = None
        if isinstance(mask, list):
            masks_list = mask
        elif torch.is_tensor(mask):
            try:
                if mask.dim() >= 3 and mask.shape[0] == len(images):
                    # slice [i:i+1, ...] to keep a [1,H,W] or [1,H,W,C] shape
                    masks_list = [mask[i : i + 1].contiguous() for i in range(len(images))]
                else:
                    masks_list = [mask]
            except Exception:
                masks_list = [mask]
        else:
            masks_list = [mask]

        if len(masks_list) not in (1, len(images)):
            raise ValueError(
                f"Mask count mismatch: got {len(masks_list)} mask(s) for {len(images)} image(s). "
                "Provide one mask (broadcast) or one per image."
            )

        def _mask_iterator():
            if len(masks_list) == 1:
                # Broadcast single mask
                for _ in range(len(images)):
                    yield masks_list[0]
            else:
                # One-to-one mapping
                for m in masks_list:
                    yield m

        _m_it = _mask_iterator()

        def run_filter(t: torch.Tensor, *, settings=settings, model=model, clip=clip, vae=vae):
            m = next(_m_it)
            processed, _ = apply_inpaint_filter_tensor(
                image=t,
                mask=m,
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
        )

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}inpaint", {
            "node": node_id,
            "dataset": dataset,
        })

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
