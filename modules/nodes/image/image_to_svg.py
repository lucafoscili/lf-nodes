import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import numpy_to_tensor, numpy_to_svg, tensor_to_numpy, tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import create_compare_node

# region LF_ImageToSVG
class LF_ImageToSVG:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor to vectorize"
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Binarization threshold for monochrome mode"
                }),
                "num_colors": (Input.INTEGER, {
                    "default": 2,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                    "tooltip": "Number of colors for quantization (1 = binary)"
                }),
                "simplify_tol": (Input.FLOAT, {
                    "default": 2.0, 
                    "min": 0.0, 
                    "max": 10.0, 
                    "step": 0.1,
                    "tooltip": "Contour simplification tolerance (Douglas-Peucker)"
                }),
                "vector_mode": (["fill", "stroke", "both"], {
                    "default": "fill",
                    "tooltip": "Render mode: fill, stroke, or both."
                }),
                "stroke_width": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Outline width"
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("svg", "svg_list", "image", "image_list", "palette", "palette_list")
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True, False, True)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        threshold: float = normalize_list_to_value(kwargs.get("threshold"))
        num_colors: int = normalize_list_to_value(kwargs.get("num_colors"))
        simplify_tol: float = normalize_list_to_value(kwargs.get("simplify_tol"))
        vector_mode: str = normalize_list_to_value(kwargs.get("vector_mode"))
        stroke_width: float = normalize_list_to_value(kwargs.get("stroke_width"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        previews: list[torch.Tensor] = []
        svgs: list[str] = []
        palettes: list[dict] = []

        for index, img in enumerate(image):
            arr = tensor_to_numpy(img)
            svg_str, proc, palette = numpy_to_svg(arr, num_colors, threshold, simplify_tol, vector_mode, stroke_width)
            preview = numpy_to_tensor(proc)

            pil_image_original = tensor_to_pil(img)
            output_file_s, subfolder_s, filename_s = resolve_filepath(
                filename_prefix="svg_s",
                image=img,
            )
            pil_image_original.save(output_file_s, format="PNG")
            filename_s = get_resource_url(subfolder_s, filename_s, "temp")

            pil_image_blended = tensor_to_pil(preview)
            output_file_t, subfolder_t, filename_t = resolve_filepath(
                filename_prefix="svg_t",
                image=preview,
            )
            pil_image_blended.save(output_file_t, format="PNG")
            filename_t = get_resource_url(subfolder_t, filename_t, "temp")

            previews.append(preview)
            svgs.append(svg_str)
            palettes.append(palette)
            nodes.append(create_compare_node(filename_s, filename_t, index))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imagetosvg", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        image_batch, image_list = normalize_output_image(previews)

        return (svgs[0], svgs, image_batch[0], image_list, palettes[0], palettes)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImageToSVG": LF_ImageToSVG,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageToSVG": "Image to SVG",
}
# endregion