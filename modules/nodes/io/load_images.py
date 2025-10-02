import os
import re
import torch

from datetime import datetime
from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.conversion import pil_to_tensor
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value, normalize_output_image
from ...utils.helpers.metadata import extract_jpeg_metadata, extract_png_metadata
from ...utils.helpers.torch import create_dummy_image_tensor
from ...utils.helpers.ui import create_masonry_node

SAFE_FILENAME_FALLBACK = "image"


def _sanitize_filename_component(name: str) -> str:
    sanitized = (name or "").strip()
    sanitized = sanitized.replace("\\", "_").replace("/", "_")
    sanitized = re.sub(r"\s+", " ", sanitized)
    sanitized = sanitized.rstrip(". ")

    while ".." in sanitized:
        sanitized = sanitized.replace("..", ".")

    sanitized = sanitized.strip()

    return sanitized or SAFE_FILENAME_FALLBACK

# region LF_LoadImages
class LF_LoadImages:
    def __init__(self):
        self._cached_images = {}

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "dir": (Input.STRING, {
                    "default":"", 
                    "tooltip": "Path to the directory containing the images to load."
                }),
                "subdir": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Indicates whether to also load images from subdirectories."
                }),
                "strip_ext": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Whether to remove file extensions from filenames."
                }),
                "load_cap": (Input.INTEGER, {
                    "default": 0, 
                    "tooltip": "Maximum number of images to load before stopping. Set 0 for an unlimited amount."
                }),
                "dummy_output": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Flag indicating whether to output a dummy image tensor and string when the list is empty."
                }),
                "cache_images": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Whether to refresh the image list each time the node is executed or to use cached images from the previous run."
                }),
                "copy_into_input_dir": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Whether to copy the loaded images into the input directory of ComfyUI. The loading is faster when this is set to False, "
                               "but this is mandatory for the preview to be displayed in the node's UI widget."
                })
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                }),
            },
            "hidden": { 
                "node_id": "UNIQUE_ID",
            } 
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, True, True, False, False, False, False, False)
    RETURN_NAMES = ("image", "image_list", "name", "creation_date", "nr", "selected_image", "selected_index", "selected_name", "metadata")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.STRING, Input.STRING, Input.INTEGER, Input.IMAGE, Input.INTEGER, Input.STRING, Input.JSON)

    def on_exec(self, **kwargs: dict):
        def select(image_list, names, sel_idx_ui, sel_name_ui):
            """
            Determine selected image, index, and name based on UI inputs.
            """
            sel_idx = sel_idx_ui
            sel_name = sel_name_ui
            sel_img = None
            # If UI index is valid
            if sel_idx is not None and 0 <= sel_idx < len(image_list):
                sel_img = image_list[sel_idx]
                sel_name = names[sel_idx]
            # Else if UI name matches
            elif sel_name_ui in names:
                sel_idx = names.index(sel_name_ui)
                sel_img = image_list[sel_idx]
                sel_name = names[sel_idx]
            # Default to first image
            else:
                sel_idx = 0 if image_list else None
                sel_name = names[0] if names else None
                sel_img = image_list[0] if image_list else None
            return sel_img, sel_idx, sel_name
    
        dir: str = normalize_list_to_value(kwargs.get("dir"))
        subdir: bool = normalize_list_to_value(kwargs.get("subdir"))
        strip_ext: bool = normalize_list_to_value(kwargs.get("strip_ext"))
        load_cap: int = normalize_list_to_value(kwargs.get("load_cap"))
        dummy_output: bool = normalize_list_to_value(kwargs.get("dummy_output"))
        cache_images: bool = normalize_list_to_value(kwargs.get("cache_images"))
        copy_into_input_dir: bool = normalize_list_to_value(kwargs.get("copy_into_input_dir"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        index = 0
        file_names: list[str] = []
        images: list[torch.Tensor] = []
        metadata_list: list[dict] = []
        output_creation_dates: list[str] = []
        selected_image = None

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        if ui_widget:
            selected_index = ui_widget.get("index", None)
            selected_name = ui_widget.get("name", None)
        else:
            selected_index = None
            selected_name = None

        cache_key = os.path.normpath(dir)

        if cache_images and cache_key in self._cached_images:
            cached_output, cached_dataset = self._cached_images[cache_key]
            img0, image_list, names, dates, count, _, _, _, metadata_list = cached_output

            sel_img, sel_idx, sel_name = select(
                image_list, names, selected_index, selected_name
            )

            new_output = (
                img0, image_list, names, dates, count,
                sel_img, sel_idx, sel_name, metadata_list
            )

            PromptServer.instance.send_sync(
                f"{EVENT_PREFIX}loadimages", {
                    "node": kwargs.get("node_id"),
                    "dataset": cached_dataset
                }
            )
            return new_output

        for root, dirs, files in os.walk(dir):
            if not subdir:
                dirs[:] = []
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image_path = os.path.join(root, file)
                    with open(image_path, 'rb') as img_file:
                        original_stem, extension = os.path.splitext(file)
                        extension = extension.lstrip('.')
                        extension_lower = extension.lower()
                        safe_stem = _sanitize_filename_component(original_stem)
                        normalized_extension = extension_lower.replace('jpg', 'jpeg')
                        display_extension = extension_lower or normalized_extension
                        safe_filename = f"{safe_stem}.{display_extension}" if display_extension else safe_stem
                        display_name = safe_stem if strip_ext else safe_filename

                        file_names.append(display_name)
              
                        file_creation_time = os.path.getctime(image_path)
                        creation_date = datetime.fromtimestamp(file_creation_time).strftime('%Y-%m-%d')
                        output_creation_dates.append(creation_date)

                        pil_image = Image.open(img_file)
                        if pil_image.format == "JPEG":
                            metadata = extract_jpeg_metadata(pil_image, original_stem)
                        elif pil_image.format == "PNG":
                            metadata = extract_png_metadata(pil_image)
                        else:
                            metadata = {"error": f"Unsupported image format for {original_stem}"}

                        rgb_img = pil_image.convert("RGB")
                        img_tensor = pil_to_tensor(rgb_img)

                        force_preview_copy = ".." in file
                        should_copy = copy_into_input_dir or force_preview_copy

                        if should_copy:
                            output_file, subfolder, resolved_filename = resolve_filepath(
                                filename_prefix=safe_stem,
                                base_output_path=get_comfy_dir("input"),
                                extension=normalized_extension,
                                add_counter=False,
                                image=img_tensor
                            )
                            url = get_resource_url(subfolder, resolved_filename, "input")
                            save_format = normalized_extension.upper() if normalized_extension else "PNG"
                            rgb_img.save(output_file, format=save_format)
                            preview_filename = resolved_filename
                        else:
                            preview_filename = safe_filename
                            url = get_resource_url(root, file, "input")

                        images.append(img_tensor)

                        metadata_list.append({
                            "file": original_stem,
                            "original_filename": file,
                            "sanitized_file": preview_filename,
                            "copied_for_preview": should_copy,
                            "metadata": metadata
                        })

                        nodes.append(create_masonry_node(preview_filename, url, index))

                        index += 1
                        if load_cap > 0 and index >= load_cap:
                            break

            if load_cap > 0 and index >= load_cap:
                break

        if dummy_output and not images:
            file_names.append("empty")
            selected_image = create_dummy_image_tensor()
            images.append(selected_image)         

        if dummy_output and images and selected_image is None:
            selected_image = create_dummy_image_tensor()

        image_batch, image_list = normalize_output_image(images)

        sel_img, sel_idx, sel_name = select(
            image_list, file_names, selected_index, selected_name
        )

        output_tuple = (image_batch[0], image_list, file_names, output_creation_dates, index, 
                        sel_img, sel_idx, sel_name, metadata_list)

        if cache_images:
            self._cached_images[cache_key] = (output_tuple, dataset)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadimages", {
            "node": kwargs.get("node_id"), 
            "dataset": dataset,
        })

        return output_tuple
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadImages": LF_LoadImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadImages": "Load images from disk",
}
# endregion