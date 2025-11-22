from PIL import Image
import numpy as np
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, resolve_uploaded_filepath
from ...utils.helpers.metadata import extract_jpeg_metadata, extract_png_metadata

# region LF_LoadMetadata
class LF_LoadMetadata:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "file_names": (Input.LF_UPLOAD, {
                    "default": "",
                    "tooltip": "List of file names separated by semicolons (e.g., file1.jpg;file2.png;file3.jpg). Leave empty if using image input."
                }),
                "upload_dir": (Input.COMBO, {
                    "default": "temp",
                    "tooltip": "Directory where the files are uploaded.",
                    "options": ["input", "output", "temp"],
                }),
                "image": (Input.IMAGE, {
                    "tooltip": "Input image to extract metadata from. If connected, upload is ignored."
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Metadata of the loaded image.",
        "List of metadata for all loaded images.",
    )
    RETURN_NAMES = ("metadata", "metadata_list")
    RETURN_TYPES = (Input.JSON, Input.JSON)

    def on_exec(self, **kwargs: dict):
        metadata_list = []

        if "image" in kwargs:
            image_tensor = kwargs["image"]
            # Assume image_tensor is torch tensor, shape (N, H, W, C), float 0-1
            for i in range(image_tensor.shape[0]):
                img_array = (image_tensor[i] * 255).clamp(0, 255).byte().cpu().numpy()
                pil_image = Image.fromarray(img_array)
                # Try to extract as JPEG first, since most images have EXIF
                try:
                    metadata = extract_jpeg_metadata(pil_image, f"input_image_{i}")
                except:
                    try:
                        metadata = extract_png_metadata(pil_image)
                    except:
                        metadata = {"error": "Failed to extract metadata from image tensor"}
                metadata_list.append({"file": f"input_image_{i}", "metadata": metadata})
            safe_send_sync("loadmetadata", {"value": "input_image"}, kwargs.get("node_id"))
        else:
            file_names: str = normalize_list_to_value(kwargs.get("file_names", ""))
            upload_dir: str = normalize_list_to_value(kwargs.get("upload_dir", "temp"))

            if upload_dir == "output":
                directory = get_comfy_dir("output")
            elif upload_dir == "input":
                directory = get_comfy_dir("input")
            else:
                directory = get_comfy_dir("temp")

            if file_names.strip():
                file_names_list = file_names.split(';')
                for file_name in file_names_list:
                    file_name = file_name.strip()
                    if not file_name:
                        continue
                    file_path, actual_name = resolve_uploaded_filepath(directory, file_name)
                    try:
                        pil_image = Image.open(file_path)
                        if pil_image.format == "JPEG":
                            metadata = extract_jpeg_metadata(pil_image, file_name)
                        elif pil_image.format == "PNG":
                            metadata = extract_png_metadata(pil_image)
                        else:
                            metadata = {"error": f"Unsupported image format for {file_name}"}
                        metadata_list.append({"file": actual_name, "metadata": metadata})
                    except Exception as e:
                        metadata_list.append({"file": file_name, "error": str(e)})
            safe_send_sync("loadmetadata", {"value": file_names}, kwargs.get("node_id"))

        return {
            "ui": {
                "lf_output": [{
                    "metadata": metadata_list,
                }],
            },
            "result": (metadata_list, metadata_list)
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadMetadata": LF_LoadMetadata,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadMetadata": "Load metadata from image",
}
# endregion
