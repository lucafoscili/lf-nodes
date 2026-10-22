"""Registered-image regional color comparison with durable diagnostic previews."""
import logging

from . import CATEGORY
from ..image.side_by_side import compose_side_by_side
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.detection.build_overlay import outline_region_masks
from ...utils.helpers.detection.region_masks import region_mask_sets
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.torch.region_color_stats import region_color_measurements
from ...utils.helpers.ui import create_cached_compare_node
from ...utils.image_regions import single_image


class LF_RegionColorStats:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_a": (Input.IMAGE, {"tooltip": "Exactly one RGB/RGBA reference sRGB image."}),
                "image_b": (Input.IMAGE, {"tooltip": "Exactly one registered RGB/RGBA sRGB image, same H,W as A."}),
                "masks": (Input.MASK, {"tooltip": "One shared region-mask set or two image-major A/B sets."}),
                "metadata": (Input.JSON, {"tooltip": "Matching lf.text-region-masks.v1 metadata; region IDs and order must agree."}),
            },
            "optional": {"ui_widget": (Input.LF_COMPARE, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.JSON, Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ("stats", "overlay", "overlay_list")
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_TOOLTIPS = (
        "lf.region-color-stats.v1: full-region Lab mean/median, B-A deltas, matched CIEDE2000 and banding heuristic.",
        "A and B with exact region outlines, side by side at their original shared resolution.",
        "Single-item list containing the side-by-side diagnostic image.",
    )

    def on_exec(self, image_a=None, image_b=None, masks=None, metadata=None, **kwargs):
        a, b = single_image(image_a, "image_a"), single_image(image_b, "image_b")
        if a.shape[-1] not in (3, 4) or b.shape[-1] not in (3, 4):
            raise ValueError("image_a and image_b must use RGB or RGBA channels.")
        if a.shape[1:3] != b.shape[1:3]:
            raise ValueError("image_a and image_b must have exactly the same H,W; resizing is not supported.")
        mask_sets, document = region_mask_sets(masks, metadata)
        if len(mask_sets) not in (1, 2):
            raise ValueError("masks must contain one shared set or exactly two image_a/image_b sets.")
        height, width = a.shape[1:3]
        if document["source_size"] != [width, height] or tuple(mask_sets.shape[-2:]) != (height, width):
            raise ValueError("masks and metadata source_size must match image_a/image_b H,W.")
        stats = region_color_measurements(a, b, mask_sets, document)
        for region in stats["regions"]:
            if region["warnings"]:
                logging.warning("LF_RegionColorStats region %s: %s", region["id"], " ".join(region["warnings"]))
        outlined_a = outline_region_masks(a, mask_sets[0])
        outlined_b = outline_region_masks(b, mask_sets[-1])
        overlay = compose_side_by_side(outlined_a, outlined_b, gap_px=8)
        batches, image_list = normalize_output_image([overlay])
        dataset = {"nodes": [create_cached_compare_node(
            outlined_a, outlined_b, index=0, title="Region outlines: A / B", debug=overlay)]}
        payload = {"dataset": dataset, "stats": stats}
        safe_send_sync("regioncolorstats", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (stats, batches[0], image_list)}


NODE_CLASS_MAPPINGS = {"LF_RegionColorStats": LF_RegionColorStats}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_RegionColorStats": "Region color stats"}
