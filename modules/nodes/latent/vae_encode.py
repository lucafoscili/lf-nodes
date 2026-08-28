from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import (
    normalize_input_image_batches,
    normalize_list_to_value,
    normalize_output_latents,
)

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
    INPUT_IS_LIST = True
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

        image_batches = normalize_input_image_batches(image_input)
        if not image_batches:
            raise RuntimeError("No valid images provided for encoding.")

        total = sum(int(image.shape[0]) for image in image_batches)

        safe_send_sync("vaeencode", {
            "value": f"## VAE Encode\n\n- Starting encode for `{total}` image(s)…",
        }, node_id)

        encoded_latents = [
            {"samples": vae.encode(image[:, :, :, :3])}
            for image in image_batches
        ]
        latent_batch, latent_list = normalize_output_latents(encoded_latents)

        batch_samples = latent_batch["samples"]
        b, c, h, w = batch_samples.shape
        output_shapes = []
        for latent in latent_list:
            shape = tuple(int(value) for value in latent["samples"].shape)
            if shape not in output_shapes:
                output_shapes.append(shape)
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
            f"- Primary compatible latent batch: `{b}x{c}x{h}x{w}`",
            f"- Per-item latent shapes: `{output_shapes}`",
            f"- Completed encoding `{total}` image(s).",
        ]

        if spatial is not None:
            log_lines.append(f"- Spatial compression (encode): `{spatial}`")
        if temporal is not None:
            log_lines.append(f"- Temporal compression (encode): `{temporal}`")

        safe_send_sync("vaeencode", {
            "value": "\n".join(log_lines),
        }, node_id)

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
