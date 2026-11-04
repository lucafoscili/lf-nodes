"""Frame a cut-out subject as a square game-style icon.

The node takes an image and the mask of its subject (for example Background
Remover's mask), fits the subject's bounding box into a square at a chosen
fill, composites it over a flat or source backdrop with an optional glow and
outline, darkens the corners, draws a bevelled rim and writes the result at a
master size and at a small display size.
"""

from __future__ import annotations

from typing import Dict, List

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_masks_for_images,
    normalize_output_image,
)
from ...utils.helpers.torch.icon_frame import BACKDROPS, frame_icon
from ...utils.helpers.ui import create_cached_compare_node


# region LF_IconFramer
class LF_IconFramer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Image (or list of images) holding the subject."}),
                "mask": (Input.MASK, {"tooltip": "Subject mask, one per image or one shared; 1 marks the subject."}),
                "master_size": (Input.INTEGER, {"default": 512, "min": 16, "max": 4096,
                    "tooltip": "Edge of the large square output, in pixels."}),
                "icon_size": (Input.INTEGER, {"default": 64, "min": 8, "max": 4096,
                    "tooltip": "Edge of the small square output, downscaled from the large one."}),
                "fill": (Input.FLOAT, {"default": 0.86, "min": 0.1, "max": 1.0, "step": 0.01,
                    "tooltip": "Share of the area inside the rim that the subject's longer side fills."}),
                "backdrop": (BACKDROPS, {"default": "color",
                    "tooltip": "color: a flat backdrop colour; source: the image's own surroundings."}),
                "backdrop_color": (Input.STRING, {"default": "#000000",
                    "tooltip": "Backdrop colour, and the fill outside the source image (#RRGGBB)."}),
                "glow_color": (Input.STRING, {"default": "#000000", "tooltip": "Colour of the glow behind the subject (#RRGGBB)."}),
                "glow_strength": (Input.FLOAT, {"default": 0.0, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Glow behind the subject; 0 turns it off."}),
                "outline": (Input.FLOAT, {"default": 0.012, "min": 0.0, "max": 0.1, "step": 0.001,
                    "tooltip": "Width of the dark outline around the subject, as a share of the edge; 0 turns it off."}),
                "outline_color": (Input.STRING, {"default": "#000000", "tooltip": "Outline colour (#RRGGBB)."}),
                "vignette": (Input.FLOAT, {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "How much the corners darken; 0 turns it off."}),
                "bevel": (Input.FLOAT, {"default": 0.05, "min": 0.0, "max": 0.2, "step": 0.005,
                    "tooltip": "Width of the bevelled rim, as a share of the edge; 0 draws no rim."}),
                "bevel_color": (Input.STRING, {"default": "#8a8a8a", "tooltip": "Base colour of the rim (#RRGGBB)."}),
                "bevel_light": (Input.FLOAT, {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.05,
                    "tooltip": "Contrast between the rim's lit top-left and shaded bottom-right sides."}),
                "threshold": (Input.FLOAT, {"default": 0.5, "min": 0.0, "max": 0.99, "step": 0.01,
                    "tooltip": "Mask value above which a pixel counts towards the subject's bounding box."}),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True, False, True)
    OUTPUT_TOOLTIPS = (
        "Framed icons at master size, as a batch.",
        "Framed icons at master size, one per input image.",
        "Framed icons at icon size, as a batch.",
        "Framed icons at icon size, one per input image.",
    )
    RETURN_NAMES = ("master", "master_list", "icon", "icon_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        images = normalize_input_image(kwargs.get("image"))
        if not images:
            raise ValueError("Icon Framer needs at least one image.")
        masks = normalize_masks_for_images(kwargs.get("mask"), len(images))
        if len(masks) == 1 and len(images) > 1:
            masks = masks * len(images)

        settings = {
            name: normalize_list_to_value(kwargs.get(name))
            for name in (
                "master_size", "icon_size", "fill", "backdrop", "backdrop_color", "glow_color",
                "glow_strength", "outline", "outline_color", "vignette", "bevel", "bevel_color",
                "bevel_light", "threshold",
            )
        }
        settings = {name: value for name, value in settings.items() if value is not None}

        masters: List[torch.Tensor] = []
        icons: List[torch.Tensor] = []
        nodes: List[dict] = []
        for index, (image, mask) in enumerate(zip(images, masks)):
            master, icon = frame_icon(image, mask, **settings)
            masters.append(master)
            icons.append(icon)
            nodes.append(create_cached_compare_node(image[..., :3], master, index=index))

        payload: Dict[str, object] = {"dataset": {"nodes": nodes}}
        safe_send_sync("iconframer", payload, normalize_list_to_value(kwargs.get("node_id")))

        master_batches, master_list = normalize_output_image(masters)
        icon_batches, icon_list = normalize_output_image(icons)
        return {
            "ui": {"lf_output": [payload]},
            "result": (master_batches[0], master_list, icon_batches[0], icon_list),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_IconFramer": LF_IconFramer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_IconFramer": "Icon Framer",
}
# endregion
