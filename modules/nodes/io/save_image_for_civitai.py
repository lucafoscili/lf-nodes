import json
import piexif
import torch

from comfy.cli_args import args
from PIL.PngImagePlugin import PngInfo
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, IMAGE_EXTENSION_COMBO, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_input_list, normalize_list_to_value
from ...utils.helpers.ui import create_masonry_node

# region LF_SaveImageForCivitAI
class LF_SaveImageForCivitAI:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input images to save."
                }),
                "filename_prefix": (Input.STRING, {
                    "default": '',
                    "tooltip": "Path and filename. Use slashes to specify directories."
                }),
                "add_timestamp": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Sets the execution time's timestamp as a suffix of the file name."
                }),
                "embed_workflow": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Whether to embed inside the images the current workflow or not."
                }),
                "extension": (IMAGE_EXTENSION_COMBO, {
                    "default": "png",
                    "tooltip": "Supported file formats."
                }),
                "quality": (Input.INTEGER, {
                    "default": 100,
                    "min": 1,
                    "max": 100,
                    "tooltip": "Quality of saved images in jpeg or webp format."
                }),
            },
            "optional": {
                "civitai_metadata": (Input.STRING, {
                    "forceInput": True,
                    "tooltip": "String containing CivitAI compatible metadata (created by the node LF_CivitAIMetadataSetup)."
                }),
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                }),
            },
            "hidden": {
                "extra_pnginfo": "EXTRA_PNGINFO",
                "node_id": "UNIQUE_ID",
                "prompt": "PROMPT",
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, False, False, False, False, False, False)
    OUTPUT_IS_LIST = (True, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "List of saved file names.",
        "CivitAI metadata string.",
    )
    RETURN_NAMES = ("file_names", "civitai_metadata")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        filename_prefix: list[str] = normalize_input_list(kwargs.get("filename_prefix"))
        extra_pnginfo: list[torch.Tensor] = normalize_list_to_value(kwargs.get("extra_pnginfo"))
        prompt: dict = normalize_list_to_value(kwargs.get("prompt"))
        add_timestamp: bool = normalize_list_to_value(kwargs.get("add_timestamp"))
        embed_workflow: bool = normalize_list_to_value(kwargs.get("embed_workflow"))
        extension: str = normalize_list_to_value(kwargs.get("extension"))
        quality: int = normalize_list_to_value(kwargs.get("quality"))
        civitai_metadata: str = normalize_list_to_value(kwargs.get("civitai_metadata", None))
        if civitai_metadata is None:
            civitai_metadata = ""

        file_names: list[str] = []

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        for index, img in enumerate(image):
            pil_img = tensor_to_pil(img)

            use_filename_list = isinstance(filename_prefix, list) and len(filename_prefix) > 1 and len(filename_prefix) == len(image)
            if use_filename_list:
                prefix = filename_prefix[index]
            else:
                prefix = filename_prefix[0]

            output_file, subfolder, filename = resolve_filepath(
                filename_prefix=prefix,
                base_output_path=get_comfy_dir("output"),
                add_timestamp=add_timestamp,
                extension=extension,
                image=img,
                add_counter=not use_filename_list
            )
            url = get_resource_url(subfolder, filename, "output")

            if extension == 'png':
                png_info = PngInfo()
                if embed_workflow and not args.disable_metadata:
                    if prompt is not None:
                        png_info.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        for key, value in extra_pnginfo.items():
                            png_info.add_text(key, json.dumps(value))

                if civitai_metadata:
                    png_info.add_text("parameters", civitai_metadata)

                pil_img.save(output_file, format="PNG", pnginfo=png_info)

            elif extension == 'jpeg':
                exif_bytes = piexif.dump({
                    "Exif": {
                        piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(civitai_metadata, encoding="unicode")
                    }
                }) if civitai_metadata else None
                pil_img.save(output_file, format="JPEG", quality=quality)
                if exif_bytes:
                    piexif.insert(exif_bytes, output_file)
            else:
                pil_img.save(output_file, format=extension.upper(), quality=quality)

            nodes.append(create_masonry_node(filename, url, index))
            file_names.append(filename)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}saveimageforcivitai", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return {
            "ui": {
                "lf_output": [{
                    "civitai_metadata": civitai_metadata,
                    "dataset": dataset,
                    "file_names": file_names,
                }],
            },
            "result": (file_names, civitai_metadata)
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SaveImageForCivitAI": LF_SaveImageForCivitAI,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveImageForCivitAI": "Save image with CivitAI-compatible metadata",
}
# endregion
