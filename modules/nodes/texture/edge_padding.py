"""Edge padding: fill a texture outside its mask from the pixels inside it."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.torch.texture_maps import EDGE_PADDING_METHOD, MASK_THRESHOLD, edge_pad
from ...utils.texture_nodes import compare_entry, mask_preview, paired_masks, texture_images, texture_result, PREVIEW_LIMIT

SCHEMA = "lf.edge-padding.v1"


class LF_EdgePadding:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Texture(s) to pad. Every channel, alpha included, is filled."}),
                "mask": (Input.MASK, {"tooltip": "Pixels to keep (above 0.5), such as a bake's UV coverage. One mask for all images or one per image, same H,W."}),
            },
            "optional": {"ui_widget": (Input.LF_COMPARE, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Fill every pixel outside the mask from the nearest pixels inside it (push-pull), so mipmaps and "
                   "filtering never blend the background into the border of a baked texture or atlas island.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "receipt", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)
    OUTPUT_TOOLTIPS = (
        "Padded texture batch; pixels inside the mask are unchanged.",
        "lf.edge-padding.v1: covered and padded pixel counts per image.",
        "The same padded textures as an authoritative list.",
    )

    def on_exec(self, image=None, mask=None, **kwargs):
        images = texture_images(image, "image")
        masks = paired_masks(mask, len(images), "mask")
        results, rows, nodes = [], [], []
        for index, (item, item_mask) in enumerate(zip(images, masks)):
            padded, row = edge_pad(item, item_mask)
            results.append(padded)
            rows.append({"index": index, **row})
            if index < PREVIEW_LIMIT:
                title = (f"Image {index + 1} | kept {row['covered_pixels']} px ({row['covered_share']:.1%}) "
                         f"| padded {row['padded_pixels']} px")
                nodes.append(compare_entry(item, padded, index, title, debug=mask_preview(item_mask)))
        receipt = {"schema": SCHEMA, "method": EDGE_PADDING_METHOD, "mask_membership": f"value > {MASK_THRESHOLD}",
                   "image_count": len(images), "images": rows}
        return texture_result(results, receipt, nodes, safe_send_sync, "edgepadding", kwargs.get("node_id"))


NODE_CLASS_MAPPINGS = {"LF_EdgePadding": LF_EdgePadding}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_EdgePadding": "Edge padding"}
