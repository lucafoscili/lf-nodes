import torch
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_latent

# region LF_VAEEncode
class LF_VAEEncode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "pixels": (Input.IMAGE, {
                    "tooltip": "The image to be encoded into latent space.",
                }),
                "vae": (Input.VAE, {
                    "tooltip": "The VAE model used for encoding the image."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, False)
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Encoded latent representation.",
        "List of encoded latent representations."
    )
    RETURN_NAMES = ("latent", "latent_list")
    RETURN_TYPES = (Input.LATENT, Input.LATENT)

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        vae = normalize_list_to_value(kwargs.get("vae"))
        image_input = kwargs.get("pixels")

        if vae is None:
            raise RuntimeError("VAE is required for encoding.")

        image_list = normalize_input_image(image_input)
        if not image_list:
            raise RuntimeError("No valid images provided for encoding.")

        total = len(image_list)

        safe_send_sync("vaeencode", {
            "value": f"## VAE Encode\n\n- Starting encode for `{total}` image(s)…",
        }, node_id)

        # Process images in batches if multiple
        if len(image_list) == 1:
            # Single image case
            pixels = image_list[0]
            latent_tensor = vae.encode(pixels[:, :, :, :3])
        else:
            # Multiple images - encode each and concatenate
            encoded_tensors = []
            for img in image_list:
                encoded = vae.encode(img[:, :, :, :3])
                encoded_tensors.append(encoded)
            latent_tensor = torch.cat(encoded_tensors, dim=0)

        latent_dict = {"samples": latent_tensor}

        b, c, h, w = latent_tensor.shape
        comp_spatial = getattr(vae, "spacial_compression_encode", None)
        comp_temporal = getattr(vae, "temporal_compression_encode", None)
        spatial = None
        temporal = None
        try:
            spatial = comp_spatial() if callable(comp_spatial) else None
        except Exception:
            spatial = None
        try:
            temporal = comp_temporal() if callable(comp_temporal) else None
        except Exception:
            temporal = None

        log_lines = [
            "## VAE Encode\n\n",
            f"- Input image count: `{total}`",
            f"- Output latent shape: `{b}x{c}x{h}x{w}`",
            f"- Completed encoding `{total}` image(s).",
        ]

        if spatial is not None:
            log_lines.append(f"- Spatial compression (encode): `{spatial}`")
        if temporal is not None:
            log_lines.append(f"- Temporal compression (encode): `{temporal}`")

        safe_send_sync("vaeencode", {
            "value": "\n".join(log_lines),
        }, node_id)

        latent_batch, latent_list = normalize_output_latent(latent_dict)

        return (latent_batch, latent_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_VAEEncode": LF_VAEEncode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VAEEncode": "VAE Encode",
}
# endregion