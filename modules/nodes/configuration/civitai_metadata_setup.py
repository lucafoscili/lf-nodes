from folder_paths import get_full_path
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, SAMPLERS, SCHEDULERS
from ...utils.helpers.api import get_embedding_hashes, get_sha256, get_lora_hashes
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import normalize_list_to_value

# region LF_CivitAIMetadataSetup
class LF_CivitAIMetadataSetup:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
            },
            "optional": {
                "model_type": (["none", "checkpoint", "unet"], {
                    "default": "none", 
                    "tooltip": "Type of model to use for metadata generation."
                }),
                "checkpoint": (get_comfy_list("checkpoints"), {
                    "default": "None", 
                    "tooltip": "Checkpoint used to generate the image (only used when model_type is 'checkpoint')."
                }),
                "unet": (get_comfy_list("unet"), {
                    "default": "None", 
                    "tooltip": "Diffusion model used to generate the image (only used when model_type is 'unet')."
                }),
                "vae": (get_comfy_list("vae"), {
                    "tooltip": "VAE used to generate the image."
                }),
                "sampler": (SAMPLERS, {
                    "default": "None", 
                    "tooltip": "Sampler used to generate the image."
                }),
                "scheduler": (SCHEDULERS, {
                    "default": "None", 
                    "tooltip": "Scheduler used to generate the image."
                }),
                "embeddings": (Input.STRING, {
                    "default": '', 
                    "multiline": True, 
                    "tooltip": "Embeddings used to generate the image."
                }),
                "lora_tags": (Input.STRING, {
                    "default": '', 
                    "multiline": True, 
                    "tooltip": "Tags of the LoRAs used to generate the image."
                }),
                "positive_prompt": (Input.STRING, {
                    "default": '', 
                    "multiline": True, 
                    "tooltip": "Prompt to generate the image."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": '', 
                    "multiline": True, 
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
                "hires_upscaler": (get_comfy_list("upscale_models"), {
                    "tooltip": "Upscale model for Hires-fix."
                }),
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
    RETURN_TYPES = ("STRING", get_comfy_list("checkpoints"), get_comfy_list("unet"), get_comfy_list("vae"),
                    SAMPLERS, SCHEDULERS, "STRING", "STRING",
                    "STRING", "STRING", "INT", "FLOAT", "INT", "FLOAT", "INT",
                    "INT", "INT", get_comfy_list("upscale_models"), "FLOAT", "JSON")

    def on_exec(self, **kwargs:dict):
        def add_metadata_node(category, item):
            """Add metadata information for a specific category."""
            if item:
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
        
        if model_type == "checkpoint" and checkpoint and checkpoint != "None":
            model_name = checkpoint
            model_hash = get_sha256(get_full_path("checkpoints", checkpoint))
            add_metadata_node("checkpoints", checkpoint)
        elif model_type == "unet" and unet and unet != "None":
            model_name = unet
            model_hash = get_sha256(get_full_path("unet", unet))
            add_metadata_node("unet", unet)

        add_metadata_node("samplers", sampler)
        add_metadata_node("schedulers", scheduler)
        add_metadata_node("upscale_models", hires_upscaler)
        add_metadata_node("vaes", vae)

        vae_hash = get_sha256(get_full_path("vae", vae)) if vae else "Unknown"
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
            f"Hires upscale: {hires_upscale or ''}, Hires upscaler: {hires_upscaler or 'Latent'}, "
            f"Lora hashes: \"{lora_hashes_str}\", TI hashes: \"{emb_hashes_str}\", Version: ComfyUI.LF Nodes"
        )

        clean_metadata_string = metadata_string.replace(".safetensors", "").replace("embedding:", "")
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}civitaimetadatasetup", {
            "node": kwargs.get("node_id"),
            "value": clean_metadata_string,
        })

        output_prompt = f"{emb_str}{positive_prompt}" if positive_prompt else ""
        
        selected_checkpoint = checkpoint if model_type == "checkpoint" else "None"
        selected_unet = unet if model_type == "unet" else "None"
        
        return (
            clean_metadata_string, selected_checkpoint, selected_unet, vae, sampler, scheduler, embeddings, lora_tags,
            output_prompt, negative_prompt, steps, denoising, clip_skip, cfg, seed,
            width, height, hires_upscaler, hires_upscale, analytics_dataset
        )
    
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CivitAIMetadataSetup": LF_CivitAIMetadataSetup,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CivitAIMetadataSetup": "CivitAI metadata setup",
}
# endregion