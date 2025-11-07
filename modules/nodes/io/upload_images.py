from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, safe_send_sync
from ...utils.helpers.conversion import pil_to_tensor
from ...utils.helpers.logic import (
    normalize_list_to_value,
    normalize_output_image,
    resolve_uploaded_filepath,
)

# region LF_UploadImages
class LF_UploadImages:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "file_names": (Input.LF_UPLOAD, {
                    "tooltip": "List of file names separated by semicolons (e.g., file1.jpg;file2.png)."
                }),
            },
            "optional": {
                "upload_dir": (Input.COMBO, {
                    "default": "temp",
                    "tooltip": "Directory where the files are uploaded.",
                    "options": ["input", "output", "temp"],
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Uploaded images.",
        "List of uploaded images.",
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        file_names: str = normalize_list_to_value(kwargs.get("file_names"))
        upload_dir: str = normalize_list_to_value(kwargs.get("upload_dir"))

        if upload_dir == "output":
            directory = get_comfy_dir("output")
        elif upload_dir == "input":
            directory = get_comfy_dir("input")
        else:
            directory = get_comfy_dir("temp")

        images: list = []
        file_list: list[str] = []

        if file_names:
            file_names_list = file_names.split(";")

            for file_name in file_names_list:
                file_name = file_name.strip()
                if not file_name:
                    continue

                file_path, actual_name = resolve_uploaded_filepath(directory, file_name)

                try:
                    with Image.open(file_path) as pil_image:
                        rgb = pil_image.convert("RGB")
                        img_tensor = pil_to_tensor(rgb)

                    images.append(img_tensor)
                    # record the actual filename used on disk
                    file_list.append(actual_name)
                except Exception as e:
                    safe_send_sync("uploadimages", {
                        "value": f"Failed to load {file_name}: {str(e)}",
                    }, kwargs.get("node_id"))

        batch_list, image_list = normalize_output_image(images) if images else ([], [])

        safe_send_sync("uploadimages", {
            "value": file_names
        }, kwargs.get("node_id"))

        first_batch = batch_list[0] if batch_list else None

        return (first_batch, image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_UploadImages": LF_UploadImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_UploadImages": "Upload images",
}
# endregion
