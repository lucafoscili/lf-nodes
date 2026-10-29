"""High-pass detail transfer: add a source's fine detail at a reference's strength."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.torch.texture_maps import detail_transfer
from ...utils.texture_nodes import (
    PREVIEW_LIMIT, absent, compare_entry, mask_preview, optional_masks, paired_images, scalar, texture_images,
    texture_result,
)

SCHEMA = "lf.detail-transfer.v1"
MODES = ["match_reference", "fixed"]


class LF_DetailTransfer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Image(s) to receive detail (sRGB)."}),
                "detail_source": (Input.IMAGE, {"tooltip": "Image whose fine lightness detail is added: one for all images or one per image, same H,W."}),
                "radius": (Input.INTEGER, {"default": 4, "min": 1, "max": 256, "step": 1,
                                           "tooltip": "Detail finer than this many pixels (box blur radius) is transferred and measured."}),
                "mode": (MODES, {"default": "match_reference",
                                 "tooltip": "match_reference: choose the gain so the result's fine detail matches reference_image's; fixed: use strength."}),
                "strength": (Input.FLOAT, {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05,
                                           "tooltip": "Gain on the source's detail in fixed mode (1.0 adds it as is). Ignored by match_reference."}),
            },
            "optional": {
                "mask": (Input.MASK, {"tooltip": "Where detail is added and measured; values weight it. Defaults to the whole image."}),
                "reference_image": (Input.IMAGE, {"tooltip": "Image whose fine detail spread the result should match (match_reference)."}),
                "reference_mask": (Input.MASK, {"tooltip": "The region of reference_image to measure. Defaults to the whole image."}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Add a detail source's fine lightness detail (its high-pass) to an image, at a fixed gain or at "
                   "the gain that makes the result's fine detail match a reference region's.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "report", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)
    OUTPUT_TOOLTIPS = (
        "Image batch with the detail added to L*; zero-weight pixels and alpha are unchanged.",
        "lf.detail-transfer.v1: the fine-detail spreads measured and the gain used, per image.",
        "The same images as an authoritative list.",
    )

    def on_exec(self, image=None, detail_source=None, mask=None, reference_image=None, reference_mask=None,
                **kwargs):
        images = texture_images(image, "image")
        count = len(images)
        sources = paired_images(detail_source, count, "detail_source")
        masks = optional_masks(mask, count, "mask")
        mode = scalar(kwargs.get("mode"), "mode")
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}, not {mode!r}.")
        radius = int(scalar(kwargs.get("radius"), "radius"))
        if radius < 1:
            raise ValueError("radius must be at least 1 pixel.")
        strength = float(scalar(kwargs.get("strength"), "strength"))
        references = ([None] * count if absent(reference_image)
                      else paired_images(reference_image, count, "reference_image"))
        reference_masks = optional_masks(reference_mask, count, "reference_mask")
        if mode == "match_reference" and references[0] is None:
            raise ValueError("mode match_reference needs reference_image.")
        results, rows, nodes = [], [], []
        for index, item in enumerate(images):
            item_mask = masks[index]
            weights = item_mask if item_mask is not None else item.new_ones(item.shape[:2])
            detailed, row = detail_transfer(item, sources[index], weights, radius=radius, mode=mode,
                                            strength=strength, reference=references[index],
                                            reference_mask=reference_masks[index])
            results.append(detailed)
            rows.append({"index": index, **row})
            if index < PREVIEW_LIMIT:
                title = (f"Image {index + 1} | gain {row['strength']:.3f} | fine L* std "
                         f"{_value(row['image_fine_l_std'])} -> {_value(row['result_fine_l_std'])}")
                if row["reference_fine_l_std"] is not None:
                    title += f" (reference {_value(row['reference_fine_l_std'])})"
                nodes.append(compare_entry(item, detailed, index, title,
                                           debug=mask_preview(item_mask) if item_mask is not None else None))
        receipt = {"schema": SCHEMA, "channel": "CIE L* (D65), decoded sRGB; alpha unchanged",
                   "method": "detail = source L* minus its box blur; L* += gain * detail * weight",
                   "gain_rule": ("the k >= 0 with k^2 source^2 + 2 k cov(image, source) + image^2 = reference^2, fine-detail "
                                 "spreads over each mask's interior; 0 when the image already matches"),
                   "mode": mode, "radius": radius, "image_count": count, "images": rows}
        return texture_result(results, receipt, nodes, safe_send_sync, "detailtransfer", kwargs.get("node_id"))


def _value(value):
    return "N/A" if value is None else f"{value:.3f}"


NODE_CLASS_MAPPINGS = {"LF_DetailTransfer": LF_DetailTransfer}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_DetailTransfer": "Detail transfer"}
