from folder_paths import get_full_path_or_raise

from . import CATEGORY
from ...utils.constants import FUNCTION, HAS_V3, Input, INT_MAX, SAMPLERS, SCHEDULERS, UNET_DIFFUSION_COMBO
from ...utils.helpers.api import get_embedding_hashes, get_sha256, get_lora_hashes
from ...utils.helpers.comfy import get_comfy_list, safe_send_sync
from ...utils.helpers.logic import is_none, normalize_list_to_value, register_selector_list


def _with_none(options) -> list[str]:
    """Add the serialized no-selection sentinel to an optional combo."""

    return ["None", *(option for option in options if option != "None")]


CHECKPOINT_VALUES = get_comfy_list("checkpoints")
UNET_VALUES = get_comfy_list("unet")
VAE_VALUES = get_comfy_list("vae")
UPSCALER_VALUES = get_comfy_list("upscale_models")


def _optional_combo(options, tooltip: str):
    values = list(options)
    if HAS_V3:
        return (Input.COMBO, {
            "default": "None",
            "options": _with_none(values),
            "tooltip": tooltip,
        })

    # Legacy Comfy encoded combo options directly as the socket type, so the
    # list must stay byte-for-byte compatible with connected selector outputs.
    # It cannot safely gain a synthetic `None` item; choose a representable
    # local default instead. `model_type` still controls whether model metadata
    # is used.
    legacy_config = {"tooltip": tooltip}
    if values:
        legacy_config["default"] = values[0]
    return (values, legacy_config)


def _is_selected(value) -> bool:
    return bool(value) and not is_none(value)


# region LF_CivitAIMetadataSetup
class LF_CivitAIMetadataSetup:
    checkpoint_values = CHECKPOINT_VALUES
    unet_values = UNET_VALUES
    vae_values = VAE_VALUES
    upscaler_values = UPSCALER_VALUES

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
            },
            "optional": {
                "model_type": (UNET_DIFFUSION_COMBO, {
                    "default": "none",
                    "tooltip": "Type of model to use for metadata generation."
                }),
                "checkpoint": _optional_combo(
                    self.checkpoint_values,
                    "Checkpoint used to generate the image (only used when model_type is 'checkpoint').",
                ),
                "unet": _optional_combo(
                    self.unet_values,
                    "Diffusion model used to generate the image (only used when model_type is 'unet').",
                ),
                "vae": _optional_combo(self.vae_values, "VAE used to generate the image."),
                "sampler": _optional_combo(SAMPLERS, "Sampler used to generate the image."),
                "scheduler": _optional_combo(SCHEDULERS, "Scheduler used to generate the image."),
                "embeddings": (Input.STRING, {
                    "default": '',
                    "tooltip": "Embeddings used to generate the image."
                }),
                "lora_tags": (Input.STRING, {
                    "default": '',
                    "tooltip": "Tags of the LoRAs used to generate the image."
                }),
                "positive_prompt": (Input.STRING, {
                    "default": '',
                    "tooltip": "Prompt to generate the image."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": '',
                    "tooltip": "Negative prompt used to generate the image."
                }),
                "steps": (Input.INTEGER, {
                    "default": 30,
                    "min": 1,
                    "max": 10000,
                    "tooltip": "Steps used to generate the image."
                }),
                "denoising": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "tooltip": "Denoising strength used to generate the image."
                }),
                "clip_skip": (Input.INTEGER, {
                    "default": -1,
                    "min": -24,
                    "max": -1,
                    "tooltip": "CLIP skip used to generate the image."
                }),
                "cfg": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 30.0,
                    "tooltip": "CFG used to generate the image."
                }),
                "seed": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "Seed used to generate the image."
                }),
                "width": (Input.INTEGER, {
                    "default": 1024,
                    "tooltip": "Width of the image."
                }),
                "height": (Input.INTEGER, {
                    "default": 1024,
                    "tooltip": "Height of the image."
                }),
                "hires_upscale": (Input.FLOAT, {
                    "default": 1.5,
                    "tooltip": "Upscale factor for Hires-fix."
                }),
                "hires_upscaler": _optional_combo(
                    self.upscaler_values,
                    "Upscale model for Hires-fix.",
                ),
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("metadata_string", "checkpoint", "unet", "vae",
                    "sampler", "scheduler", "embeddings", "lora_tags",
                    "full_pos_prompt", "neg_prompt", "steps", "denoising", "clip_skip", "cfg", "seed",
                    "width", "height", "hires_upscaler", "hires_upscale", "analytics_dataset")
    OUTPUT_TOOLTIPS = (
        "Metadata string for the image.",
        "Checkpoint model used for the image.",
        "UNet model used for the image.",
        "VAE model used for the image.",
        "Sampler used for the image.",
        "Scheduler used for the image.",
        "Embeddings used for the image.",
        "LoRA tags used for the image.",
        "Full positive prompt used for the image.",
        "Negative prompt used for the image.",
        "Steps used for the image.",
        "Denoising strength used for the image.",
        "CLIP skip used for the image.",
        "CFG used for the image.",
        "Seed used for the image.",
        "Width of the image.",
        "Height of the image.",
        "Hires upscaler used for the image.",
        "Hires upscale factor used for the image.",
        "Analytics dataset for the image."
    )
    RETURN_TYPES = (Input.STRING,
                    CHECKPOINT_VALUES,
                    UNET_VALUES,
                    VAE_VALUES,
                    SAMPLERS,
                    SCHEDULERS,
                    Input.STRING, Input.STRING,
                    Input.STRING, Input.STRING, Input.INTEGER, Input.FLOAT, Input.INTEGER, Input.FLOAT, Input.INTEGER,
                    Input.INTEGER, Input.INTEGER, UPSCALER_VALUES, Input.FLOAT, Input.JSON)

    def on_exec(self, **kwargs:dict):
        def add_metadata_node(category, item):
            """Add metadata information for a specific category."""
            if _is_selected(item):
                analytics_dataset["nodes"].append({
                    "children": [{"id": item, "value": item}],
                    "id": category
                })

        cfg: float = normalize_list_to_value(kwargs.get("cfg"))
        checkpoint: str = normalize_list_to_value(kwargs.get("checkpoint"))
        clip_skip: int = normalize_list_to_value(kwargs.get("clip_skip"))
        denoising: float = normalize_list_to_value(kwargs.get("denoising"))
        embeddings: str = normalize_list_to_value(kwargs.get("embeddings"))
        height: int = normalize_list_to_value(kwargs.get("height"))
        hires_upscale: float = normalize_list_to_value(kwargs.get("hires_upscale"))
        hires_upscaler: str = normalize_list_to_value(kwargs.get("hires_upscaler"))
        lora_tags: str = normalize_list_to_value(kwargs.get("lora_tags"))
        model_type: str = normalize_list_to_value(kwargs.get("model_type"))
        negative_prompt: str = normalize_list_to_value(kwargs.get("negative_prompt"))
        positive_prompt: str = normalize_list_to_value(kwargs.get("positive_prompt"))
        sampler: str = normalize_list_to_value(kwargs.get("sampler"))
        scheduler: str = normalize_list_to_value(kwargs.get("scheduler"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        steps: int = normalize_list_to_value(kwargs.get("steps"))
        unet: str = normalize_list_to_value(kwargs.get("unet"))
        vae: str = normalize_list_to_value(kwargs.get("vae"))
        width: int = normalize_list_to_value(kwargs.get("width"))

        analytics_dataset: dict = {"nodes": []}

        model_name = "Unknown"
        model_hash = "Unknown"

        if model_type == "checkpoint" and _is_selected(checkpoint):
            model_name = checkpoint
            model_hash = get_sha256(get_full_path_or_raise("checkpoints", checkpoint))
            add_metadata_node("checkpoints", checkpoint)
        elif model_type == "unet" and _is_selected(unet):
            model_name = unet
            model_hash = get_sha256(get_full_path_or_raise("unet", unet))
            add_metadata_node("unet", unet)

        add_metadata_node("samplers", sampler)
        add_metadata_node("schedulers", scheduler)
        add_metadata_node("upscale_models", hires_upscaler)
        add_metadata_node("vaes", vae)

        vae_hash = get_sha256(get_full_path_or_raise("vae", vae)) if _is_selected(vae) else "Unknown"
        emb_hashes_str = ", ".join(get_embedding_hashes(embeddings, analytics_dataset)) if embeddings else ""
        lora_hashes_str = ", ".join(get_lora_hashes(lora_tags, analytics_dataset)) if lora_tags else ""

        emb_str = f"{embeddings}, " if embeddings else ""
        lora_str = f", {lora_tags}" if lora_tags else ""

        # Metadata string generation
        metadata_string = (
            f"{emb_str}{positive_prompt or ''}{lora_str}\n"
            f"Negative prompt: {negative_prompt or ''}\n"
            f"Steps: {steps or ''}, Sampler: {sampler or ''}, Schedule type: {scheduler or ''}, CFG scale: {cfg or ''}, "
            f"Seed: {seed or ''}, Size: {width or ''}x{height or ''}, "
            f"Denoising strength: {denoising or ''}, Clip skip: {abs(clip_skip) or ''}, "
            f"VAE hash: {vae_hash}, "
            f"Model hash: {model_hash}, Model: {model_name}, "
            f"Hires upscale: {hires_upscale or ''}, Hires upscaler: {hires_upscaler if _is_selected(hires_upscaler) else 'Latent'}, "
            f"Lora hashes: \"{lora_hashes_str}\", TI hashes: \"{emb_hashes_str}\", Version: ComfyUI.LF Nodes"
        )

        clean_metadata_string = metadata_string.replace(".safetensors", "").replace("embedding:", "")

        safe_send_sync("civitaimetadatasetup", {
            "value": clean_metadata_string,
        }, kwargs.get("node_id"))

        output_prompt = f"{emb_str}{positive_prompt}" if positive_prompt else ""

        selected_checkpoint = checkpoint if model_type == "checkpoint" else "None"
        selected_unet = unet if model_type == "unet" else "None"

        return (
            clean_metadata_string, selected_checkpoint, selected_unet, vae, sampler, scheduler, embeddings, lora_tags,
            output_prompt, negative_prompt, steps, denoising, clip_skip, cfg, seed,
            width, height, hires_upscaler, hires_upscale, analytics_dataset
        )

# endregion

_CIVITAI_CHECKPOINT_LIST = register_selector_list(
    LF_CivitAIMetadataSetup,
    lambda: get_comfy_list("checkpoints"),
    attr_name="checkpoint_values",
    return_index=1,
)
_CIVITAI_UNET_LIST = register_selector_list(
    LF_CivitAIMetadataSetup,
    lambda: get_comfy_list("unet"),
    attr_name="unet_values",
    return_index=2,
)
_CIVITAI_VAE_LIST = register_selector_list(
    LF_CivitAIMetadataSetup,
    lambda: get_comfy_list("vae"),
    attr_name="vae_values",
    return_index=3,
)
_CIVITAI_UPSCALER_LIST = register_selector_list(
    LF_CivitAIMetadataSetup,
    lambda: get_comfy_list("upscale_models"),
    attr_name="upscaler_values",
    return_index=17,
)

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CivitAIMetadataSetup": LF_CivitAIMetadataSetup,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CivitAIMetadataSetup": "CivitAI metadata setup",
}
# endregion
