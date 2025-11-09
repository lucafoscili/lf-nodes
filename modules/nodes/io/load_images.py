import os
import torch

from datetime import datetime
from PIL import Image

from . import CATEGORY
from ...utils.constants import FUNCTION, IMAGE_FILE_EXTENSIONS, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import (
    ensure_external_preview,
    get_comfy_dir,
    resolve_filepath,
    resolve_input_directory_path,
    safe_send_sync,
)
from ...utils.helpers.conversion import pil_to_tensor
from ...utils.helpers.logic import (
    SAFE_FILENAME_FALLBACK,
    normalize_json_input,
    normalize_list_to_value,
    normalize_output_image,
    sanitize_filename,
)
from ...utils.helpers.editing import resolve_image_selection
from ...utils.helpers.metadata import extract_jpeg_metadata, extract_png_metadata
from ...utils.helpers.torch import create_dummy_image_tensor
from ...utils.helpers.ui import create_masonry_node

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
                    "tooltip": "When enabled the node reuses the last scan for the same settings, skipping disk traversal until parameters change."
                }),
                "copy_into_input_dir": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Create sanitized copies inside ComfyUI's input folder for reuse/export. Previews now work without this, but keep it on if you want dedicated duplicates."
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
    OUTPUT_TOOLTIPS = (
        "Loaded image tensor.",
        "List of loaded image tensors.",
        "Name of the loaded image.",
        "Creation date of the loaded image.",
        "Number of loaded images.",
        "Selected image tensor.",
        "Index of the selected image.",
        "Name of the selected image.",
        "Metadata of the images.",
    )
    RETURN_NAMES = ("image", "image_list", "name", "creation_date", "nr", "selected_image", "selected_index", "selected_name", "metadata")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.STRING, Input.STRING, Input.INTEGER, Input.IMAGE, Input.INTEGER, Input.STRING, Input.JSON)

    def on_exec(self, **kwargs: dict):
        dir: str = normalize_list_to_value(kwargs.get("dir"))
        subdir: bool = normalize_list_to_value(kwargs.get("subdir"))
        strip_ext: bool = normalize_list_to_value(kwargs.get("strip_ext"))
        load_cap: int = normalize_list_to_value(kwargs.get("load_cap"))
        dummy_output: bool = normalize_list_to_value(kwargs.get("dummy_output"))
        cache_images: bool = normalize_list_to_value(kwargs.get("cache_images"))
        copy_into_input_dir: bool = normalize_list_to_value(kwargs.get("copy_into_input_dir"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        base_input_dir = get_comfy_dir("input")
        resolved_dir, resolved_directory, is_external_dir = resolve_input_directory_path(dir)
        if resolved_dir is not None and not os.path.isdir(resolved_dir):
            resolved_dir = None

        index = 0
        file_names: list[str] = []
        images: list[torch.Tensor] = []
        metadata_list: list[dict] = []
        output_creation_dates: list[str] = []
        selected_image = None

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        raw_directory_value = dir if isinstance(dir, str) else ""
        navigation_directory: dict[str, object] = {
            "raw": raw_directory_value,
            "relative": (resolved_directory or "") if resolved_directory is not None else "",
            "is_external": is_external_dir,
        }
        if resolved_dir:
            navigation_directory["resolved"] = resolved_dir

        dataset["navigation"] = {"directory": navigation_directory}

        if ui_widget:
            selected_index = ui_widget.get("index", None)
            selected_name = ui_widget.get("name", None)
        else:
            selected_index = None
            selected_name = None

        cache_key_base = resolved_dir or (dir or "")
        try:
            normalized_cache_key = os.path.normpath(cache_key_base)
        except Exception:
            normalized_cache_key = cache_key_base
        cache_key = "|".join(
            [
                normalized_cache_key,
                str(subdir),
                str(strip_ext),
                str(load_cap),
                str(copy_into_input_dir),
                str(is_external_dir),
            ]
        )

        if cache_images and cache_key in self._cached_images:
            cached_output, cached_dataset = self._cached_images[cache_key]
            img0, image_list, names, dates, count, _, _, _, metadata_list = cached_output

            sel_idx_input = selected_index if isinstance(selected_index, int) else None
            sel_name_input = selected_name if isinstance(selected_name, str) else None

            sel_img, sel_idx, sel_name = resolve_image_selection(
                image_list,
                names,
                selection_index=sel_idx_input,
                selection_name=sel_name_input,
            )

            new_output = (
                img0, image_list, names, dates, count,
                sel_img, sel_idx, sel_name, metadata_list
            )

            safe_send_sync(
                "loadimages", {
                    "dataset": cached_dataset
                },
                kwargs.get("node_id")
            )
            return new_output

        if resolved_dir:
            for root, dirs, files in os.walk(resolved_dir):
                if not subdir:
                    dirs[:] = []

                relative_to_dir = os.path.relpath(root, resolved_dir)
                relative_to_dir = "" if relative_to_dir == "." else relative_to_dir.replace("\\", "/")
                combined_subfolder = "/".join(
                    [part for part in [resolved_directory, relative_to_dir] if part]
                )

                for file in files:
                    if not file.lower().endswith(IMAGE_FILE_EXTENSIONS):
                        continue

                    image_path = os.path.join(root, file)
                    if not os.path.isfile(image_path):
                        continue

                    with open(image_path, "rb") as img_file:
                        original_stem, extension = os.path.splitext(file)
                        extension_lower = extension.lstrip(".").lower()

                        sanitized_full = sanitize_filename(
                            file,
                            default_ext=extension_lower or "png",
                        )
                        safe_stem, safe_ext = os.path.splitext(sanitized_full)
                        safe_stem = safe_stem or SAFE_FILENAME_FALLBACK
                        safe_ext = safe_ext.lstrip(".") or (extension_lower or "png")

                        normalized_extension = safe_ext.replace("jpg", "jpeg")
                        display_extension = extension_lower or normalized_extension
                        safe_filename = f"{safe_stem}.{display_extension}" if display_extension else safe_stem
                        display_name = safe_stem if strip_ext else safe_filename

                        file_names.append(display_name)

                        try:
                            file_creation_time = os.path.getctime(image_path)
                            creation_date = datetime.fromtimestamp(file_creation_time).strftime("%Y-%m-%d")
                        except OSError:
                            creation_date = ""
                        output_creation_dates.append(creation_date)

                        with Image.open(img_file) as pil_image:
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
                        copied_for_preview = False

                        if is_external_dir:
                            try:
                                preview_subfolder, preview_filename = ensure_external_preview(root, file)
                                copied_for_preview = True
                            except FileNotFoundError:
                                continue
                            url = get_resource_url(preview_subfolder, preview_filename, "input")
                        elif should_copy:
                            filename_prefix = f"{combined_subfolder}/{safe_stem}" if combined_subfolder else safe_stem
                            output_file, subfolder, resolved_filename = resolve_filepath(
                                filename_prefix=filename_prefix,
                                base_output_path=base_input_dir,
                                extension=normalized_extension,
                                add_counter=False,
                                image=img_tensor,
                            )
                            url = get_resource_url(subfolder, resolved_filename, "input")
                            save_format = normalized_extension.upper() if normalized_extension else "PNG"
                            rgb_img.save(output_file, format=save_format)
                            preview_filename = resolved_filename
                            copied_for_preview = True
                        else:
                            preview_filename = safe_filename
                            target_subfolder = combined_subfolder
                            url = get_resource_url(target_subfolder, file, "input")

                        images.append(img_tensor)

                        metadata_list.append(
                            {
                                "file": original_stem,
                                "original_filename": file,
                                "sanitized_file": preview_filename,
                                "copied_for_preview": copied_for_preview,
                                "metadata": metadata,
                            }
                        )

                        nodes.append(create_masonry_node(preview_filename, url, index))

                        index += 1
                        if load_cap > 0 and index >= load_cap:
                            break

                if load_cap > 0 and index >= load_cap:
                    break

        placeholder_tensor = None
        if not images:
            placeholder_tensor = selected_image if isinstance(selected_image, torch.Tensor) else create_dummy_image_tensor()
            if dummy_output:
                images.append(placeholder_tensor)
                if not file_names:
                    file_names.append("empty")
                if not output_creation_dates:
                    output_creation_dates.append("")
                metadata_list.append(
                    {
                        "file": file_names[-1],
                        "original_filename": None,
                        "sanitized_file": file_names[-1],
                        "copied_for_preview": False,
                        "metadata": {"info": "Generated placeholder image."},
                    }
                )
                selected_image = placeholder_tensor

        if selected_image is None and images:
            selected_image = images[0]

        image_batch, image_list = normalize_output_image(images) if images else ([], [])

        sel_idx_input = selected_index if isinstance(selected_index, int) else None
        sel_name_input = selected_name if isinstance(selected_name, str) else None

        sel_img, sel_idx, sel_name = resolve_image_selection(
            image_list,
            file_names,
            selection_index=sel_idx_input,
            selection_name=sel_name_input,
        )

        if image_batch:
            primary_image = image_batch[0]
        elif sel_img is not None and isinstance(sel_img, torch.Tensor):
            primary_image = sel_img
        elif isinstance(selected_image, torch.Tensor):
            primary_image = selected_image
        elif isinstance(placeholder_tensor, torch.Tensor):
            primary_image = placeholder_tensor
        else:
            primary_image = create_dummy_image_tensor()

        if sel_img is None or not isinstance(sel_img, torch.Tensor):
            if isinstance(selected_image, torch.Tensor):
                sel_img = selected_image
            elif isinstance(placeholder_tensor, torch.Tensor):
                sel_img = placeholder_tensor
            else:
                sel_img = primary_image

        output_tuple = (
            primary_image,
            image_list,
            file_names,
            output_creation_dates,
            index,
            sel_img,
            sel_idx,
            sel_name,
            metadata_list,
        )

        if cache_images:
            self._cached_images[cache_key] = (output_tuple, dataset)

        safe_send_sync("loadimages", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

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
