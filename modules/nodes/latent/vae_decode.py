from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import (
    normalize_input_latent_batches,
    normalize_list_to_value,
    normalize_output_image,
)

# region LF_VAEDecode
class LF_VAEDecode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "samples": (Input.LATENT, {
                    "tooltip": "The latent to be decoded.",
                }),
                "vae": (Input.VAE, {
                    "tooltip": "The VAE model used for decoding the latent."
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
        "Decoded image.",
        "List of decoded images."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        vae = normalize_list_to_value(kwargs.get("vae"))
        latent_input = kwargs.get("samples")

        if vae is None:
            raise RuntimeError("VAE is required for decoding.")

        latent_batches = normalize_input_latent_batches(latent_input)
        total = sum(int(latent["samples"].shape[0]) for latent in latent_batches)

        safe_send_sync("vaedecode", {
            "value": f"## VAE Decode\n\n- Starting decode for `{total}` sample(s)…",
        }, node_id)

        decoded_images = []
        for latent in latent_batches:
            images = vae.decode(latent["samples"])
            if hasattr(images, "dim") and images.dim() == 5:
                images = images.reshape(
                    -1,
                    images.shape[-3],
                    images.shape[-2],
                    images.shape[-1],
                )
            _, single_images = normalize_output_image(images)
            decoded_images.extend(single_images)

        batch_groups, image_list = normalize_output_image(decoded_images)
        primary_batch = batch_groups[0]
        b, h, w, c = (
            int(primary_batch.shape[0]),
            int(primary_batch.shape[1]),
            int(primary_batch.shape[2]),
            int(primary_batch.shape[3]),
        )
        output_shapes = []
        for image in image_list:
            shape = tuple(int(value) for value in image.shape)
            if shape not in output_shapes:
                output_shapes.append(shape)
        comp_spatial = getattr(vae, "spacial_compression_decode", None)
        comp_temporal = getattr(vae, "temporal_compression_decode", None)
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
            "## VAE Decode\n\n",
            f"- Input latent keys: `{list(latent_batches[0].keys())}`",
            f"- Primary compatible image batch: `{b}x{h}x{w}x{c}`",
            f"- Per-item image shapes: `{output_shapes}`",
            f"- Completed decoding `{total}` sample(s).",
        ]

        if spatial is not None:
            log_lines.append(f"- Spatial compression (decode): `{spatial}`")
        if temporal is not None:
            log_lines.append(f"- Temporal compression (decode): `{temporal}`")

        safe_send_sync("vaedecode", {
            "value": "\n".join(log_lines),
        }, node_id)

        return (primary_batch, image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_VAEDecode": LF_VAEDecode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VAEDecode": "VAE Decode",
}
# endregion
