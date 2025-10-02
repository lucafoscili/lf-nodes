import torch
import torch.nn.functional as F

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import get_tokenizer_from_clip, resolve_filepath
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import (
    get_otsu_threshold,
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_image,
    normalize_output_mask,
)
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import encode_text_for_sdclip, get_text_encoder_from_clip
from ...utils.helpers.ui import create_compare_node

# region LF_CreateMask
class LF_CreateMask:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "processor": ("*", {
                    "tooltip": "CLIPSegProcessor from LF_LoadHFModel (segmentation model).",
                }),
                "model":     ("*", {
                    "tooltip": "CLIPSegForImageSegmentation from LF_LoadHFModel (segmentation model).",
                }),
                "image": (Input.IMAGE, {
                    "tooltip": "Image tensor to segment."
                }),
                "prompt": (Input.STRING, {
                    "tooltip": "Text prompt for mask."
                }),
                "threshold_mode": (["fixed", "relative", "otsu"], {
                    "default": "otsu",
                    "tooltip": (
                        "Thresholding mode: 'fixed' uses the exact threshold value; "
                        "'relative' scales threshold by max probability; 'otsu' auto-computes."
                    )
                })
            },
            "optional": {
                "clip": (Input.CLIP, {
                    "tooltip": 
                    f"Optional Stable-Diffusion CLIP model:\n "
                    f"⚠️ Embeddings from this CLIP will not perfectly match the segmentation head—"
                    f"expect degraded mask accuracy unless you fine-tune or insert an adapter."
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Binarization threshold on mask probabilities (0→1). Lower to include more pixels."
                }),
                "relative_scale": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Fraction of peak probability to use when in 'relative' mode."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default":{}
                })
            },
            "hidden": {"node_id":"UNIQUE_ID"}
        }

    RETURN_TYPES   = ("MASK", "MASK", "IMAGE", "IMAGE")
    RETURN_NAMES   = ("mask", "mask_list", "image", "image_list")
    CATEGORY       = CATEGORY
    FUNCTION       = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True)

    def on_exec(self, **kwargs):
        self._temp_cache.cleanup()
        
        images = normalize_input_image(kwargs["image"])
        proc = normalize_list_to_value(kwargs["processor"])
        seg_model = normalize_list_to_value(kwargs["model"])
        prompt = normalize_list_to_value(kwargs["prompt"])
        clip = normalize_list_to_value(kwargs.get("clip", None))
        mode = normalize_list_to_value(kwargs.get("threshold_mode", "otsu"))
        fixed_thresh = normalize_list_to_value(kwargs.get("threshold", 0.5))
        rel_scale = normalize_list_to_value(kwargs.get("relative_scale", 0.5))

        seg_model.eval()
        device = next(seg_model.parameters()).device

        mask_images, mask_tensors, nodes = [], [], []
        dataset = { "nodes": nodes }

        for idx, img_tensor in enumerate(images):
            pil_img = tensor_to_pil(img_tensor)

            if clip is not None:
                text_encoder = get_text_encoder_from_clip(clip)
                tokenizer   = get_tokenizer_from_clip(clip)
                _, token_ids, attn_mask = encode_text_for_sdclip(
                    text_encoder, tokenizer, prompt, device
                )

                img_inputs   = proc(images=pil_img, return_tensors="pt")
                pixel_values = img_inputs.pixel_values.to(device)

                with torch.no_grad():
                    outputs = seg_model(
                        pixel_values=pixel_values,
                        input_ids=token_ids,
                        attention_mask=attn_mask
                    )
            else:
                inputs = proc(text=prompt, images=pil_img, return_tensors="pt")
                inputs = {k:v.to(device) for k,v in inputs.items()}
                with torch.no_grad():
                    outputs = seg_model(**inputs)

            probs = torch.sigmoid(outputs.logits)
            mask_prob = probs[0,0] if probs.ndim==4 else probs[0]

            if mode == "relative":
                thresh = mask_prob.max().item() * rel_scale
            elif mode == "otsu":
                prob_map = mask_prob.cpu().numpy() 
                thresh = get_otsu_threshold(prob_map)
            else:
                thresh = fixed_thresh

            binary = (mask_prob >= thresh).float().unsqueeze(0).unsqueeze(0)
            binary = binary.to(device)
            H, W = img_tensor.shape[1], img_tensor.shape[2]
            up = F.interpolate(binary, size=(H, W), mode="nearest")
            mask_image = up.permute(0, 2, 3, 1)
            mask_rgb = mask_image.repeat(1, 1, 1, 3)
            mask_images.append(mask_rgb)
            mask_tensors.append(up[:, 0])

            orig_f, so, no = resolve_filepath("mask_orig",
                                              image=img_tensor,
                                              temp_cache=self._temp_cache)
            tensor_to_pil(img_tensor).save(orig_f, "PNG")
            mo, sm, nm = resolve_filepath("mask_bin",
                                          image=mask_rgb,
                                          temp_cache=self._temp_cache)
            tensor_to_pil(mask_rgb).save(mo, "PNG")
            nodes.append(create_compare_node(get_resource_url(so,no,"temp"),
                                               get_resource_url(sm,nm,"temp"),
                                               idx))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}createmask", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        image_batch, image_list = normalize_output_image(mask_images)
        mask_batch, mask_list = normalize_output_mask(mask_tensors)

        return (mask_batch[0], mask_list, image_batch[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CreateMask": LF_CreateMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CreateMask": "Create Mask",
}
# endregion