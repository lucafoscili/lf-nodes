import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.filters import line_effect
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import process_and_save_image

# region LF_Line
class LF_Line:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor to draw a line upon."
                }),
                "start_x": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Horizontal position to begin the line drawing, expressed as a value between 0 and 1."
                }),
                "start_y": (Input.FLOAT, {
                    "default": 0,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Vertical position to begin the line drawing, expressed as a value between 0 and 1."
                }),
                "end_x": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Horizontal position to end the line drawing, expressed as a value between 0 and 1."
                }),
                "end_y": (Input.FLOAT, {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Vertical position to end the line drawing, expressed as a value between 0 and 1."
                }),
                "size": (Input.INTEGER, {
                    "default": 10,
                    "min": 1,
                    "max": 500,
                    "step": 1,
                    "tooltip": "Diameter of the line in pixels."
                }),
                "color": (Input.STRING, {
                    "default": "FF0000",
                    "tooltip": "Hex color of the line."
                }),
                "opacity": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Opacity of the line."
                }),
                "smooth": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Draws a smooth line."
                }),
            },
            "optional": {
                "mid_x": (Input.FLOAT, {
                    "default": 0.25,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Horizontal midpoint of the line, expressed as a value between 0 and 1."
                }),
                "mid_y": (Input.FLOAT, {
                    "default": 0.25,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Vertical midpoint of the line, expressed as a value between 0 and 1."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Image tensor with line effect applied.",
        "List of image tensors with line effect applied."
    )
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        start_x: float = normalize_list_to_value(kwargs.get("start_x", 0))
        start_y: float = normalize_list_to_value(kwargs.get("start_y", 0))
        end_x: float = normalize_list_to_value(kwargs.get("end_x", 1))
        end_y: float = normalize_list_to_value(kwargs.get("end_y", 1))
        mid_x: float = normalize_list_to_value(kwargs.get("mid_x", (start_x + end_x) / 2))
        mid_y: float = normalize_list_to_value(kwargs.get("mid_y", (start_y + end_y) / 2))
        size: int = normalize_list_to_value(kwargs.get("size"))
        color: str = normalize_list_to_value(kwargs.get("color"))
        smooth: bool = normalize_list_to_value(kwargs.get("smooth"))
        opacity: float = normalize_list_to_value(kwargs.get("opacity"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        points: list[tuple] = [(start_x, start_y)]
        if smooth:
            points.append((mid_x, mid_y))
        points.append((end_x, end_y))

        processed_images = process_and_save_image(
            images=image,
            filter_function=line_effect,
            filter_args={
                'points': points,
                'size': size,
                'color': color,
                'opacity': opacity,
                "smooth": smooth
            },
            filename_prefix="line",
            nodes=nodes,
            temp_cache=self._temp_cache,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}line", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Line": LF_Line,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Line": "Line",
}
# endregion
