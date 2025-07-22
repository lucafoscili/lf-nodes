import os
import re
import timm
import torch

from folder_paths import get_folder_paths, get_full_path
from huggingface_hub import snapshot_download
from pathlib import Path
from tqdm.auto import tqdm
from timm.data import create_transform, resolve_data_config
from torchvision import transforms
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation

import comfy.sd
import comfy.utils

from ..utils.constants import ANY, BASE64_PNG_PREFIX, CATEGORY_PREFIX, EVENT_PREFIX, FUNCTION, Input, INT_MAX, NOTIFY_COMBO, SAMPLERS, SCHEDULERS
from ..utils.helpers import get_comfy_list, get_embedding_hashes, get_lora_hashes, get_sha256, normalize_input_image, normalize_list_to_value,  prepare_model_dataset, process_model, tensor_to_base64

from server import PromptServer

CATEGORY = f"{CATEGORY_PREFIX}/Configuration"

class PromptServerTqdm(tqdm):
    """
    A tqdm progress bar subclass that logs model download progress and sends updates via PromptServer.

    Args:
        *args: Positional arguments passed to the tqdm constructor.
        node_id (str): Identifier for the node associated with this progress.
        event_name (str): Name of the event to send updates for.
        model_id (str): Identifier of the model being processed.
        log_lines (list[str]): List to append log messages to.
        **kwargs: Additional keyword arguments passed to the tqdm constructor.

    Methods:
        update(n=1):
            Advances the progress bar by n steps, logs progress messages, and sends updates to the PromptServer.
    """
    def __init__(self, *args, node_id: str, event_name: str, model_id: str, log_lines: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.node_id = node_id
        self.event_name = event_name
        self.log_lines = log_lines
        self.model_id = model_id

    def update(self, n=1):
        super().update(n)

        if self.n == 1:
            self.log_lines.append(f"Checking model cache... **{self.model_id}**")

        if self.n > 1:
            pct = self.format_dict.get('percentage', 0)
            rate = self.format_dict.get('rate_fmt', '')
            elapsed = int(self.format_dict.get('elapsed', 0))
            remaining= int(self.format_dict.get('remaining', 0))

            self.log_lines.append(
                f"_⏳ Downloading model files: {self.n}/{self.total} "
                f"({pct:.0f}% • {rate}/s • elapsed {elapsed}s • ETA {remaining}s)_"
            )
        
        log = "".join(self.log_lines)

        PromptServer.instance.send_sync(self.event_name, {
            "node": self.node_id, 
            "value": log
        })
            
def create_custom_tqdm(node_id: str, event_name: str, model_id: str, log_lines: list[str]):
    """
    Creates a custom subclass of PromptServerTqdm with pre-configured initialization parameters.

    Args:
        node_id (str): The unique identifier for the node.
        event_name (str): The name of the event associated with the tqdm instance.
        model_id (str): The identifier for the model being used.
        log_lines (list[str]): A list of log lines to be associated with the tqdm instance.

    Returns:
        type: A subclass of PromptServerTqdm with the provided parameters set in its constructor.
    """
    class CustomTqdm(PromptServerTqdm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args,
                             node_id=node_id,
                             event_name=event_name,
                             model_id=model_id,
                             log_lines=log_lines,
                             **kwargs)
    return CustomTqdm

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

# region LF_ControlPanel
class LF_ControlPanel:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "ui_widget": (Input.LF_CONTROL_PANEL, {
                    "default": {}
                })
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ()

    def on_exec(self, **kwargs: dict):
        return ()
# endregion

# region LF_LoadCLIPSegModel
class LF_LoadCLIPSegModel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": (Input.STRING, {
                    "default": "clip_vision",
                    "tooltip": "Folder to download the model to. This folder must be in the ComfyUI directory."
                }),
                "model_id": (Input.STRING, {
                    "default": "CIDAS/clipseg-rd64-refined",
                    "tooltip": "HuggingFace CLIPSeg model ID."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": {"node_id":"UNIQUE_ID"}
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("*", "*")
    RETURN_NAMES = ("processor", "model")

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        folder = normalize_list_to_value(kwargs["folder"])
        model_id = normalize_list_to_value(kwargs["model_id"])
        base_dir = get_folder_paths(folder)[0]

        safe_name = model_id.replace("/", "--")
        model_dir = os.path.join(base_dir, safe_name)
        exists = os.path.isdir(model_dir) and os.listdir(model_dir)

        log_lines = []
        if exists:
            log_lines.append(f"- ✅ Model already present → `{model_dir}`")
        else:
            log_lines.append(f"- ⏳ Downloading **{model_id}** → `{model_dir}`")

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadclipsegmodel", {
            "node": node_id, 
            "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
        })

        try:
            processor = CLIPSegProcessor.from_pretrained(model_dir)
            model = CLIPSegForImageSegmentation.from_pretrained(model_dir).eval()
            log_lines.append(f"- ✅ Loaded processor & model from {model_dir}")
        except Exception as e:
            raise RuntimeError(f"- ❌ Failed to load CLIPSeg from {model_dir}: {e}")
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadclipsegmodel", {
            "node": node_id, 
            "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
        })

        return (processor, model)
# endregion

# region LF_LoadWD14Model
class LF_LoadWD14Model:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": (Input.STRING, {
                    "default": "SmilingWolf/wd-vit-large-tagger-v3",
                    "tooltip": "HuggingFace model ID."
                }),
                "architecture": (Input.STRING, {
                    "default": "vit_large_patch16_224",
                    "tooltip": "timm model architecture string for WD14 (e.g., vit_large_patch14_224, vit_huge_patch14_224, vit_base_patch16_224, vit_large_patch16_224, etc.)"
                }),
                "num_classes": (Input.INTEGER, {
                    "default": 10861,
                    "tooltip": "Number of classes/tags for WD14 model (e.g., 10861, 8965, 5400, etc.)"
                }),
                "image_size": (Input.INTEGER, {
                    "default": 448,
                    "tooltip": "Input image size for WD14 model (e.g., 448, 224, etc.)"
                }),
                "mean": (Input.STRING, {
                    "default": "0.5,0.5,0.5",
                    "tooltip": "Mean for normalization (comma-separated, e.g., 0.5,0.5,0.5)"
                }),
                "std": (Input.STRING, {
                    "default": "0.5,0.5,0.5",
                    "tooltip": "Std for normalization (comma-separated, e.g., 0.5,0.5,0.5)"
                }),                                    
            },
            "optional": {            
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("*", "*")
    RETURN_NAMES = ("processor", "model")

    def on_exec(self, **kwargs):
        node_id: str  = kwargs.get("node_id")
        model_id: str = normalize_list_to_value(kwargs["model_id"])
        arch: str = normalize_list_to_value(kwargs.get("architecture", "vit_large_patch16_224"))
        num_classes: int = normalize_list_to_value(kwargs.get("num_classes", 10861))
        image_size: int = normalize_list_to_value(kwargs.get("image_size", 448))
        mean: str = normalize_list_to_value(kwargs.get("mean", "0.5,0.5,0.5"))
        std: str = normalize_list_to_value(kwargs.get("std", "0.5,0.5,0.5"))

        event_name: str = f"{EVENT_PREFIX}loadwd14model"
        log_lines: list[str] = ["## Load WD14 Model\n\n"]
        float_mean: list[float] = [float(x) for x in mean.split(",")]
        float_std: list[float] = [float(x) for x in std.split(",")]

        CustomTqdm = create_custom_tqdm(node_id, event_name, model_id, log_lines)

        snapshot_download(
            repo_id=model_id,
            tqdm_class=CustomTqdm,
            local_dir_use_symlinks=False
        )

        try:
            model = timm.create_model(arch, pretrained=False, num_classes=num_classes)
            state_dict = timm.models.load_state_dict_from_hf(model_id)
            state_dict = {k.replace("model.", ""): v for k, v in state_dict.items()}
            model.load_state_dict(state_dict)
            model.eval()
            processor = transforms.Compose([
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=float_mean,
                    std=float_std
                ),
            ])
            log_lines.append(f"- ✅ Model loaded! (standard timm)")
        except Exception as e:
            log_lines.append(f"- ⚠️ Standard timm load failed: {e}\n\n")
            try:
                # fallback: let timm pull both architecture & weights from HF Hub
                model = timm.create_model(f"hf_hub:{model_id}", pretrained=True, num_classes=num_classes)
                model.eval()
                # some timm versions use .pretrained_cfg, others .default_cfg
                cfg_attr = getattr(model, "pretrained_cfg", None) or getattr(model, "default_cfg", {})
                data_config = resolve_data_config(cfg_attr, model=model)
                processor = create_transform(**data_config)
                log_lines.append(f"- ✅ Model loaded from HuggingFace Hub via timm ({model_id})")
            except Exception as e:
                raise RuntimeError(f"- ❌ Failed to load model: {e}")

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadwd14model", {
            "node": node_id, 
            "value": "".join(log_lines)
        })

        return (processor, model)
# endregion

# region LF_LoadLoraTags
class LF_LoadLoraTags:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "get_civitai_info": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Attempts to retrieve more info about the models from CivitAI."
                }),
                "model": (Input.MODEL, {
                    "tooltip": "The main model to apply the LoRA to."
                }),
                "clip": (Input.CLIP, {
                    "tooltip": "The CLIP model to modify."
                }),
                "tags": (Input.STRING, {
                    "default": '', 
                    "multiline": True, 
                    "tooltip": "Text containing LoRA tags, e.g., <lora:example:1.0>"
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CARDS_WITH_CHIP, {
                    "default": ""
                })
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("model", "clip")
    RETURN_TYPES = ("MODEL", "CLIP")

    def on_exec(self, **kwargs: dict):
        def get_lora_weights(tag_content: str):
            name = tag_content[1]
            try:
                m_weight = float(tag_content[2]) if len(tag_content) > 2 else 1.0
                c_weight = float(tag_content[3]) if len(tag_content) > 3 else m_weight
            except ValueError:
                return None, None, None

            lora_files = get_comfy_list("loras")

            lora_name:str = None
            for lora_file in lora_files:
                if Path(lora_file).name.startswith(name) or lora_file.startswith(name):
                    lora_name = lora_file
                    break
                
            return lora_name, m_weight, c_weight
        def load_lora_file(lora_path: str):
            lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
            return lora
        def add_chip(value: str):
            return { "icon": "x", 
                     "description": "Failed to load this LoRA.", 
                     "id": value, 
                     "value": value } 
        
        clip = normalize_list_to_value(kwargs.get("clip"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        model = normalize_list_to_value(kwargs.get("model"))
        tags: str = normalize_list_to_value(kwargs.get("tags"))

        regex = r"\<[0-9a-zA-Z\:\_\-\.\s\/\(\)\\\\]+\>"
        found_tags: list[str] = re.findall(regex, tags)

        api_flags: list[bool] = []
        nodes: list[dict] = []
        chip_dataset: dict =  { "nodes": nodes }
        datasets: list[dict] =  []
        hashes: list[str] = []
        lora_paths: list[str] = []
        lora_status: dict = {}

        if not found_tags:

            PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadloratags", {
                "node": kwargs.get("node_id"),
                "apiFlags": [False],
            })

            return (model, clip)

        for tag in found_tags:
            tag_content = tag[1:-1].split(":")
            if tag_content[0] != 'lora' or len(tag_content) < 2:
                nodes.append(add_chip(tag_content))
                continue

            lora_name, m_weight, c_weight = get_lora_weights(tag_content)
            if not lora_name:
                nodes.append(add_chip(lora_name))
                lora_status[tag_content[1]] = False
                continue

            if lora_name in lora_status:
                print(f"LoRA '{lora_name}' is already loaded, skipping.")
                continue

            lora_path = get_full_path("loras", lora_name)
            lora = load_lora_file(lora_path)

            model, clip = comfy.sd.load_lora_for_models(model, clip, lora, m_weight, c_weight)

            lora_status[lora_name] = True

            lora_data = process_model("lora", lora_name, "loras")
            name = lora_data["model_name"]
            hash = lora_data["model_hash"]
            path = lora_data["model_path"]
            base64 = lora_data["model_base64"]
            saved_info = lora_data["saved_info"]

            hashes.append(hash)
            lora_paths.append(path)

            if saved_info:
                datasets.append(saved_info)
                api_flags.append(False)
            else:
                datasets.append(prepare_model_dataset(name, hash, base64, path))
                api_flags.append(get_civitai_info)

        if not len(nodes):
            nodes.append({ "icon": "check",
                           "description": "Each LoRA has been loaded successfully!", 
                           "id": "0", 
                           "value": "LoRA loaded successfully!" })
            

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadloratags", {
            "node": kwargs.get("node_id"),
            "datasets": datasets,
            "hashes": hashes,
            "apiFlags": api_flags,
            "paths": lora_paths,
            "chip": chip_dataset
        })

        return (model, clip)
# endregion

# region LF_Notify
class LF_Notify:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "any": (ANY, {
                    "tooltip": "Pass-through data."
                }),
                "title": (Input.STRING, {
                    "default": "ComfyUI - LF Nodes", 
                    "tooltip": "The title displayed by the notification."
                }),
                "message": (Input.STRING, {
                    "default": "Your ComfyUI workflow sent you a notification!", 
                    "multiline": True, 
                    "tooltip": "The message displayed by the notification."
                }),
                "on_click_action": (NOTIFY_COMBO, {
                    "tooltip": "Action triggered when clicking on the notification."
                }),
                "silent": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "The notifications will be displayed without triggering a sound effect."
                }),
            },
            "optional": {
                "image": (Input.IMAGE, {
                    "tooltip": "Image displayed in the notification."
                }),
                "tag": (Input.STRING, {
                    "default": '', "tooltip": "Used to group notifications (old ones with the same tag will be replaced)."
                }),
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("any", "any_list")
    RETURN_TYPES = (ANY, ANY)

    def on_exec(self, **kwargs: dict):
        any: str = normalize_list_to_value(kwargs.get("any"))
        on_click_action: str = normalize_list_to_value(kwargs.get("on_click_action"))
        title: str = normalize_list_to_value(kwargs.get("title"))
        message: str = normalize_list_to_value(kwargs.get("message"))
        silent: str = normalize_list_to_value(kwargs.get("silent"))
        tag: str = normalize_list_to_value(kwargs.get("tag"))
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image", []))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}notify", {
            "node": kwargs.get("node_id"), 
            "title": title,
            "message": message,
            "action": on_click_action.lower(),
            "image": f"{BASE64_PNG_PREFIX}{tensor_to_base64(image[0])}" if image else None,
            "silent": silent,
            "tag": tag
        })

        return (any, any)
# endregion

NODE_CLASS_MAPPINGS = {
    "LF_CivitAIMetadataSetup": LF_CivitAIMetadataSetup,
    "LF_ControlPanel": LF_ControlPanel,
    "LF_LoadCLIPSegModel": LF_LoadCLIPSegModel,
    "LF_LoadWD14Model": LF_LoadWD14Model,
    "LF_LoadLoraTags": LF_LoadLoraTags,
    "LF_Notify": LF_Notify,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CivitAIMetadataSetup": "CivitAI metadata setup",
    "LF_ControlPanel": "Control panel",
    "LF_LoadCLIPSegModel": "Load CLIPSeg model",
    "LF_LoadWD14Model": "Load WD14 model",
    "LF_LoadLoraTags": "Load LoRA tags",
    "LF_Notify": "Notify",
}