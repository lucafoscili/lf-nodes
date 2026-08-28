import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, MASK_SHAPE_COMBO
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.detection import build_region_mask
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_mask,
)
from ...utils.helpers.ui import cache_generated_preview, create_compare_node


def _is_region_metadata(value) -> bool:
    return isinstance(value, dict) and (
        "regions" in value or "selected_region" in value
    )


def _region_metadata_for_images(value, image_count: int) -> list:
    """Pair detector metadata with images, broadcasting only singleton inputs."""

    if isinstance(value, tuple):
        value = list(value)
    if isinstance(value, dict):
        return [value] * image_count
    if not isinstance(value, list) or not value:
        raise ValueError("region_meta must contain region metadata.")

    if len(value) == 1 and _is_region_metadata(value[0]):
        return [value[0]] * image_count
    if len(value) == image_count and all(_is_region_metadata(item) for item in value):
        return value

    raw_regions = value[0] if len(value) == 1 and isinstance(value[0], (list, tuple)) else value
    if (
        raw_regions
        and all(isinstance(item, dict) for item in raw_regions)
        and not any(_is_region_metadata(item) for item in raw_regions)
    ):
        metadata = {"regions": list(raw_regions), "selected_region": None}
        return [metadata] * image_count

    raise ValueError(
        "region_meta must be one metadata item to broadcast or one item per input image."
    )


def _select_target_region(region_meta, region_index: int):
    regions = region_meta.get("regions") or []
    selected_region = region_meta.get("selected_region")
    if region_index >= 0 and region_index < len(regions):
        return regions[region_index]
    if selected_region is not None:
        return selected_region
    if regions:
        return regions[0]
    raise ValueError("No region available to build a mask.")

# region LF_RegionMask
class LF_RegionMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Image whose dimensions define the mask canvas."
                }),
                "region_meta": (Input.REGION_META, {
                    "tooltip": "Region metadata dict/list produced by detection nodes."
                }),
            },
            "optional": {
                "region_index": (Input.INTEGER, {
                    "default": -1,
                    "min": -1,
                    "max": 256,
                    "tooltip": "Index of the region to use; -1 selects the region flagged as selected."
                }),
                "shape": (MASK_SHAPE_COMBO, {
                    "default": "rectangle",
                    "tooltip": "Mask shape to carve inside the bounding box."
                }),
                "padding": (Input.FLOAT, {
                    "default": 0.05,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Padding factor relative to region size."
                }),
                "padding_px": (Input.FLOAT, {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 1024.0,
                    "step": 0.5,
                    "tooltip": "Additional padding in absolute pixels."
                }),
                "feather": (Input.FLOAT, {
                    "default": 0.05,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Feather amount; 0 keeps a hard edge."
                }),
                "invert": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Invert the mask (highlight everything outside the region)."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {},
                    "tooltip": "Optional compare widget preview (original vs mask)."
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True, False, True)
    OUTPUT_TOOLTIPS = (
        "Region mask output.",
        "Region mask output as a list.",
        "Metadata of the first region used to build the mask.",
        "Metadata for every region used across the input batch.",
    )
    RETURN_NAMES = ("mask", "mask_list", "region", "region_list")
    RETURN_TYPES = (Input.MASK, Input.MASK, Input.REGION_META, Input.REGION_META)

    def on_exec(self, **kwargs):
        node_id = kwargs.get("node_id")
        images = normalize_input_image(kwargs["image"])
        if not images:
            raise ValueError("image must contain at least one image.")
        image_tensor = images[0]

        region_metadata = _region_metadata_for_images(
            kwargs.get("region_meta"),
            len(images),
        )
        region_index = int(normalize_list_to_value(kwargs.get("region_index", -1)))
        shape = normalize_list_to_value(kwargs.get("shape", "rectangle")) or "rectangle"
        padding = float(normalize_list_to_value(kwargs.get("padding", 0.0)))
        padding_px = float(normalize_list_to_value(kwargs.get("padding_px", 0.0)))
        feather = float(normalize_list_to_value(kwargs.get("feather", 0.0)))
        invert = bool(normalize_list_to_value(kwargs.get("invert", False)))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}
        masks_4d: list[torch.Tensor] = []
        target_regions: list[dict] = []
        for index, (img, metadata) in enumerate(zip(images, region_metadata)):
            target_region = _select_target_region(metadata, region_index)

            mask_4d = build_region_mask(
                img,
                target_region,
                padding=padding,
                padding_px=padding_px,
                feather=feather,
                shape=shape,
                invert=invert,
            )
            masks_4d.append(mask_4d)

            mask_rgb = mask_4d.repeat(1, 1, 1, 3)
            source_preview = cache_generated_preview(img)
            mask_preview = cache_generated_preview(mask_rgb)
            nodes.append(
                create_compare_node(mask_preview.url, source_preview.url, index)
            )

            region_summary = dict(target_region)
            region_summary["mask_shape"] = shape
            region_summary["padding"] = padding
            region_summary["padding_px"] = padding_px
            region_summary["feather"] = feather
            region_summary["invert"] = invert
            target_regions.append(region_summary)

        payload = {"dataset": dataset}
        safe_send_sync("regionmask", payload, node_id)

        mask_batch, mask_list = normalize_output_mask(masks_4d)

        if mask_batch:
            primary_mask = mask_batch[0]
        else:
            height = int(image_tensor.shape[1])
            width = int(image_tensor.shape[2])
            primary_mask = torch.zeros((1, height, width), device=image_tensor.device, dtype=torch.float32)
            mask_list = [primary_mask]

        return {
            "ui": {"lf_output": [payload]},
            "result": (primary_mask, mask_list, target_regions[0], target_regions),
        }
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_RegionMask": LF_RegionMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_RegionMask": "Region Mask",
}
# endregion
