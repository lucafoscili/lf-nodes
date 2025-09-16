import os

from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import extract_jpeg_metadata, extract_png_metadata, get_comfy_dir, normalize_list_to_value

# region LF_LoadMetadata
class LF_LoadMetadata:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "file_names": (Input.LF_UPLOAD, {
                    "tooltip": "List of file names separated by semicolons (e.g., file1.jpg;file2.png;file3.jpg)."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                }),
            },
            "hidden": { 
                "node_id": "UNIQUE_ID",
            } 
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("metadata", "metadata_list")
    RETURN_TYPES = ("JSON",)

    def on_exec(self, **kwargs: dict):
        file_names: str = normalize_list_to_value(kwargs.get("file_names"))

        input_dir = get_comfy_dir("input")
        metadata_list: list[str] = []
        metadata = ""

        if file_names:
            file_names_list = file_names.split(';')

            for file_name in file_names_list:
                file_path = os.path.join(input_dir, file_name.strip())

                try:
                    pil_image = Image.open(file_path)

                    if pil_image.format == "JPEG":
                        metadata = extract_jpeg_metadata(pil_image, file_name)
                    elif pil_image.format == "PNG":
                        metadata = extract_png_metadata(pil_image)
                    else:
                        metadata = {"error": f"Unsupported image format for {file_name}"}

                    metadata_list.append({"file": file_name, "metadata": metadata})
                except Exception as e:
                    metadata_list.append({"file": file_name, "error": str(e)})

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadmetadata", {
            "node": kwargs.get("node_id"),
            "value": metadata,
        })

        return (metadata_list, metadata_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadMetadata": LF_LoadMetadata,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadMetadata": "Load metadata from image",
}
# endregion