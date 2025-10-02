from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_input_latent, normalize_list_to_value, normalize_output_image

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
    INPUT_IS_LIST = (True, False)
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        vae = normalize_list_to_value(kwargs.get("vae"))
        latent_input = kwargs.get("samples")

        if vae is None:
            raise RuntimeError("VAE is required for decoding.")

        latent_dict = normalize_input_latent(latent_input)
        latent_tensor = latent_dict.get("samples")

        if latent_tensor is None:
            raise RuntimeError("Invalid latent input: missing 'samples'.")
        total = int(latent_tensor.shape[0]) if hasattr(latent_tensor, "dim") and latent_tensor.dim() >= 1 else 1

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}vaedecode", {
            "node": node_id,
            "value": f"## VAE Decode\n\n- Starting decode for `{total}` sample(s)…",
        })

        images = vae.decode(latent_tensor)
        if hasattr(images, "dim") and images.dim() == 5:
            images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])

        b, h, w, c = int(images.shape[0]), int(images.shape[1]), int(images.shape[2]), int(images.shape[3])
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
            f"- Input latent keys: `{list(latent_dict.keys())}`",
            f"- Output image shape: `{b}x{h}x{w}x{c}`",
            f"- Completed decoding `{total}` sample(s).",
        ]

        if spatial is not None:
            log_lines.append(f"- Spatial compression (decode): `{spatial}`")
        if temporal is not None:
            log_lines.append(f"- Temporal compression (decode): `{temporal}`")

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}vaedecode", {
            "node": node_id,
            "value": "\n".join(log_lines),
        })

        batch_list, image_list = normalize_output_image(images)
        
        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_VAEDecode": LF_VAEDecode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VAEDecode": "VAE Decode",
}
# endregion
