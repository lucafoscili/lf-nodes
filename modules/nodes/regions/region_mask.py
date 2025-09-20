import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, EVENT_PREFIX
from ...utils.helpers import (
    normalize_input_image,
    normalize_list_to_value,
    normalize_output_image,
    tensor_to_pil,
    resolve_filepath,
    get_resource_url,
    create_compare_node,
)
from ...utils.regions import build_region_mask

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
                "shape": (Input.STRING, {
                    "default": "rectangle",
                    "choices": ["rectangle", "ellipse"],
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
    INPUT_IS_LIST = (True, True, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_TYPES = ("MASK", "MASK", "REGION_META")
    RETURN_NAMES = ("mask", "maske_list", "region")

    def on_exec(self, **kwargs):
        node_id = kwargs.get("node_id")
        images = normalize_input_image(kwargs["image"])
        image_tensor = images[0]

        region_meta = normalize_list_to_value(kwargs.get("region_meta"))
        region_index = int(normalize_list_to_value(kwargs.get("region_index", -1)))
        shape = normalize_list_to_value(kwargs.get("shape", "rectangle")) or "rectangle"
        padding = float(normalize_list_to_value(kwargs.get("padding", 0.0)))
        padding_px = float(normalize_list_to_value(kwargs.get("padding_px", 0.0)))
        feather = float(normalize_list_to_value(kwargs.get("feather", 0.0)))
        invert = bool(normalize_list_to_value(kwargs.get("invert", False)))

        regions = []
        selected_region = None
        if isinstance(region_meta, dict):
            regions = region_meta.get("regions") or []
            selected_region = region_meta.get("selected_region")
        elif isinstance(region_meta, (list, tuple)):
            regions = list(region_meta)

        target_region = None
        if region_index >= 0 and regions:
            if region_index < len(regions):
                target_region = regions[region_index]
        if target_region is None and selected_region is not None:
            target_region = selected_region
        if target_region is None and regions:
            target_region = regions[0]
        if target_region is None:
            raise ValueError("No region available to build a mask.")
        
        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}
        masks_4d: list[torch.Tensor] = []
        for _index, img in enumerate(images):

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

            orig_path, orig_sub, orig_name = resolve_filepath("region_source", image=image_tensor)
            tensor_to_pil(image_tensor).save(orig_path, "PNG")

            mask_rgb = mask_4d.repeat(1, 1, 1, 3)
            mask_path, mask_sub, mask_name = resolve_filepath("region_mask", image=mask_rgb)
            tensor_to_pil(mask_rgb).save(mask_path, "PNG")

            url_a = get_resource_url(orig_sub, orig_name, "temp")
            url_b = get_resource_url(mask_sub, mask_name, "temp")
            nodes.append(create_compare_node(url_b, url_a, _index))

        # Attach mask summary for downstream nodes
        target_region = dict(target_region)
        target_region.setdefault("mask_shape", shape)
        target_region.setdefault("padding", padding)
        target_region.setdefault("padding_px", padding_px)
        target_region.setdefault("feather", feather)
        target_region.setdefault("invert", invert)

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}regionmask",
            {"node": node_id, "dataset": dataset},
        )

        mask_batch_4d, mask_list_4d = normalize_output_image(masks_4d)

        mask_batch = [batch.squeeze(-1).contiguous() for batch in mask_batch_4d]
        mask_list = [mask.squeeze(-1).contiguous() for mask in mask_list_4d]

        if mask_batch:
            primary_mask = mask_batch[0]
        else:
            height = int(image_tensor.shape[1])
            width = int(image_tensor.shape[2])
            primary_mask = torch.zeros((1, height, width), device=image_tensor.device, dtype=torch.float32)
            mask_list = [primary_mask]

        return (primary_mask, mask_list, target_region)


NODE_CLASS_MAPPINGS = {
    "LF_RegionMask": LF_RegionMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_RegionMask": "Region Mask",
}



