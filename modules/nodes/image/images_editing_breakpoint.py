import json
import os
import time
import torch

from PIL import Image
from server import PromptServer
from urllib.parse import urlparse, parse_qs

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX, SAMPLERS, SCHEDULERS
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.conversion import pil_to_tensor, tensor_to_pil
from ...utils.helpers.editing import clear_editing_context, register_editing_context
from ...utils.helpers.logic import normalize_conditioning, normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import create_masonry_node

# region LF_ImagesEditingBreakpoint
class LF_ImagesEditingBreakpoint:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Batch of images."
                }),
            },
            "optional": {
                "model": (Input.MODEL, {
                    "tooltip": "Optional diffusion model reused by inpaint edits."
                }),
                "clip": (Input.CLIP, {
                    "tooltip": "Optional CLIP encoder reused by inpaint edits."
                }),
                "vae": (Input.VAE, {
                    "tooltip": "Optional VAE reused by inpaint edits."
                }),
                "sampler": (SAMPLERS, {
                    "tooltip": "Optional sampler reused by inpaint edits.",
                    "default": "dpmpp_2m"
                }),
                "scheduler": (SCHEDULERS, {
                    "tooltip": "Optional scheduler reused by inpaint edits.",
                    "default": "normal"
                }),
                "cfg": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 30.0,
                    "step": 0.1,
                    "tooltip": "CFG scale used as the starting value for inpaint edits."
                }),
                "positive_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional positive prompt used to pre-fill the inpaint editor."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional negative prompt used to pre-fill the inpaint editor."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional positive conditioning to reuse during inpaint edits."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional negative conditioning to reuse during inpaint edits."
                }),
                "ui_widget": (Input.LF_IMAGE_EDITOR, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True)
    RETURN_NAMES = ("image", "image_list", "orig_image", "orig_image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE")

    def on_exec(self, **kwargs):
        def wait_for_editing_completion(json_file_path):
            while True:
                with open(json_file_path, 'r', encoding='utf-8') as json_file:
                    dataset = json.load(json_file)

                status_column: dict = next((col for col in dataset.get("columns", []) if col.get("id") == "status"), None)
                if status_column and status_column.get("title") == "completed":
                    break
                
                time.sleep(0.5)

            return dataset

        model_value = normalize_list_to_value(kwargs.get("model"))
        clip_value = normalize_list_to_value(kwargs.get("clip"))
        vae_value = normalize_list_to_value(kwargs.get("vae"))
        sampler_value = normalize_list_to_value(kwargs.get("sampler"))
        scheduler_value = normalize_list_to_value(kwargs.get("scheduler"))

        cfg_raw = normalize_list_to_value(kwargs.get("cfg"))
        try:
            cfg_value = float(cfg_raw) if cfg_raw is not None else None
        except (TypeError, ValueError):
            cfg_value = None

        seed_raw = normalize_list_to_value(kwargs.get("seed"))
        try:
            seed_value = int(seed_raw) if seed_raw not in (None, "") else None
        except (TypeError, ValueError):
            seed_value = None

        positive_prompt_raw = normalize_list_to_value(kwargs.get("positive_prompt"))
        positive_prompt_value = str(positive_prompt_raw) if positive_prompt_raw not in (None, "") else ""

        negative_prompt_raw = normalize_list_to_value(kwargs.get("negative_prompt"))
        negative_prompt_value = str(negative_prompt_raw) if negative_prompt_raw not in (None, "") else ""

        positive_conditioning_value = normalize_conditioning(kwargs.get("positive_conditioning"))
        negative_conditioning_value = normalize_conditioning(kwargs.get("negative_conditioning"))

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        columns: list[dict] = []
        nodes: list[dict] = []
        dataset: dict = {"columns": columns, "nodes": nodes}

        for index, img in enumerate(image):
            pil_image = tensor_to_pil(img)
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix="edit_breakpoint", 
                image=img
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")
            nodes.append(create_masonry_node(filename, url, index))

        temp_json_file: str = os.path.join(get_comfy_dir("temp"), f"{kwargs.get('node_id')}_edit_dataset.json")
        dataset["context_id"] = temp_json_file

        columns.append({"id": "path", "title": temp_json_file})
        columns.append({"id": "status", "title": "pending"})

        inpaint_defaults: dict[str, object] = {}
        if cfg_value is not None:
            inpaint_defaults["cfg"] = cfg_value
        if seed_value is not None and seed_value >= 0:
            inpaint_defaults["seed"] = seed_value
        if positive_prompt_value:
            inpaint_defaults["positive_prompt"] = positive_prompt_value
        if negative_prompt_value:
            inpaint_defaults["negative_prompt"] = negative_prompt_value

        if inpaint_defaults:
            dataset.setdefault("defaults", {})["inpaint"] = inpaint_defaults

        register_editing_context(
            temp_json_file,
            model=model_value,
            clip=clip_value,
            vae=vae_value,
            sampler=sampler_value,
            scheduler=scheduler_value,
            cfg=cfg_value,
            seed=seed_value,
            positive_prompt=positive_prompt_value or None,
            negative_prompt=negative_prompt_value or None,
            positive_conditioning=positive_conditioning_value,
            negative_conditioning=negative_conditioning_value,
        )
        with open(temp_json_file, 'w', encoding='utf-8') as json_file:
            json.dump(dataset, json_file, ensure_ascii=False, indent=4)

        try:
            PromptServer.instance.send_sync(
                f"{EVENT_PREFIX}imageseditingbreakpoint",
                {
                    "node": kwargs.get("node_id"),
                    "value": temp_json_file,
                },
            )
            dataset = wait_for_editing_completion(temp_json_file)
        finally:
            clear_editing_context(temp_json_file)

        edited_images = []
        for node in dataset["nodes"]:
            image_url = node.get("cells").get("lfImage").get("lfValue")
            
            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)
            
            filename = query_params.get("filename", [None])[0]
            file_type = query_params.get("type", [None])[0]
            subfolder = query_params.get("subfolder", [None])[0]

            image_path = os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

            pil_image = Image.open(image_path).convert("RGB")
            edited_images.append(pil_to_tensor(pil_image))

        batch_list, image_list = normalize_output_image(image)
        edited_batch_list, edited_image_list = normalize_output_image(edited_images)

        return (edited_batch_list[0], edited_image_list, batch_list[0], image_list)      
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImagesEditingBreakpoint": LF_ImagesEditingBreakpoint,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImagesEditingBreakpoint": "Images editing breakpoint",
}
# endregion