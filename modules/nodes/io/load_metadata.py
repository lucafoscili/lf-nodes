from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir
from ...utils.helpers.logic import normalize_list_to_value, resolve_uploaded_filepath
from ...utils.helpers.metadata import extract_jpeg_metadata, extract_png_metadata

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
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Metadata of the loaded image.",
        "List of metadata for all loaded images.",
    )
    RETURN_NAMES = ("metadata", "metadata_list")
    RETURN_TYPES = (Input.JSON, Input.JSON)

    def on_exec(self, **kwargs: dict):
        file_names: str = normalize_list_to_value(kwargs.get("file_names"))
        upload_dir: str = normalize_list_to_value(kwargs.get("upload_dir"))

        if upload_dir == "output":
            directory = get_comfy_dir("output")
        elif upload_dir == "input":
            directory = get_comfy_dir("input")
        else:
            directory = get_comfy_dir("temp")

        metadata_list: list[str] = []
        metadata = ""

        if file_names:
            file_names_list = file_names.split(';')

            for file_name in file_names_list:
                file_name = file_name.strip()
                if not file_name:
                    continue

                file_path, actual_name = resolve_uploaded_filepath(directory, file_name)

                try:
                    pil_image = Image.open(file_path)

                    if pil_image.format == "JPEG":
                        # pass the original requested name for metadata context, but
                        # store the actual filename used for the returned entry
                        metadata = extract_jpeg_metadata(pil_image, file_name)
                    elif pil_image.format == "PNG":
                        metadata = extract_png_metadata(pil_image)
                    else:
                        metadata = {"error": f"Unsupported image format for {file_name}"}

                    metadata_list.append({"file": actual_name, "metadata": metadata})
                except Exception as e:
                    metadata_list.append({"file": file_name, "error": str(e)})

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadmetadata", {
            "node": kwargs.get("node_id"),
            "value": file_names,
        })

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
