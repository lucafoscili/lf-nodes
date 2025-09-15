import json
import os
import time
import torch

from PIL import Image
from server import PromptServer
from urllib.parse import urlparse, parse_qs

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import create_masonry_node, get_comfy_dir, get_resource_url, normalize_input_image, normalize_output_image, pil_to_tensor, resolve_filepath, tensor_to_pil

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
                "ui_widget": (Input.LF_IMAGE_EDITOR, {
                    "default": {}
                })
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

        columns.append({"id": "path", "title": temp_json_file})
        columns.append({"id": "status", "title": "pending"})
        
        with open(temp_json_file, 'w', encoding='utf-8') as json_file:
            json.dump(dataset, json_file, ensure_ascii=False, indent=4)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imageseditingbreakpoint", {
            "node": kwargs.get("node_id"),
            "value": temp_json_file,
        })

        dataset = wait_for_editing_completion(temp_json_file)

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