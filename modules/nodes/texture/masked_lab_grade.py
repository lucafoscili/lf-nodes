"""Masked Lab grade: give a region the colour mean and spread of a reference region."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.torch.texture_maps import lab_grade
from ...utils.texture_nodes import (
    PREVIEW_LIMIT, compare_entry, mask_preview, paired_images, paired_masks, scalar, texture_images, texture_result,
)

SCHEMA = "lf.masked-lab-grade.v1"
APPLY_TO = ["mask", "image"]


class LF_MaskedLabGrade:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Image(s) to grade (sRGB)."}),
                "mask": (Input.MASK, {"tooltip": "The region to measure and grade; values weight both. One mask for all images or one per image."}),
                "reference_image": (Input.IMAGE, {"tooltip": "Image holding the colour to match: one for all images or one per image."}),
                "reference_mask": (Input.MASK, {"tooltip": "The reference region on reference_image; values weight the measurement."}),
                "min_stretch": (Input.FLOAT, {"default": 0.25, "min": 0.01, "max": 4.0, "step": 0.05,
                                              "tooltip": "Lowest factor applied to each Lab channel's spread (reference spread / image spread, clamped)."}),
                "max_stretch": (Input.FLOAT, {"default": 1.0, "min": 0.01, "max": 4.0, "step": 0.05,
                                              "tooltip": "Highest spread factor. 1.0 may narrow the spread but never widens it, so noise is not amplified."}),
                "amount": (Input.FLOAT, {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05,
                                         "tooltip": "Share of the grade applied: 0 keeps the image, 1 matches the reference."}),
                "apply_to": (APPLY_TO, {"default": "mask",
                                        "tooltip": "mask: blend the grade by the mask's values; image: grade every pixel by the masked measurement."}),
            },
            "optional": {"ui_widget": (Input.LF_COMPARE, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Shift and scale a masked region's CIE Lab mean and spread to a reference region's, the spread "
                   "change bounded. Matches a patch, a decal or a texture to the colour around it.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "report", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)
    OUTPUT_TOOLTIPS = (
        "Graded image batch; pixels with zero weight and alpha are unchanged.",
        "lf.masked-lab-grade.v1: Lab mean and spread of the image, reference and result regions, and the stretch.",
        "The same graded images as an authoritative list.",
    )

    def on_exec(self, image=None, mask=None, reference_image=None, reference_mask=None, **kwargs):
        images = texture_images(image, "image")
        count = len(images)
        masks = paired_masks(mask, count, "mask")
        references = paired_images(reference_image, count, "reference_image")
        reference_masks = paired_masks(reference_mask, count, "reference_mask")
        settings = {name: float(scalar(kwargs.get(name), name)) for name in ("min_stretch", "max_stretch", "amount")}
        apply_to = scalar(kwargs.get("apply_to"), "apply_to")
        if apply_to not in APPLY_TO:
            raise ValueError(f"apply_to must be one of {APPLY_TO}, not {apply_to!r}.")
        results, rows, nodes = [], [], []
        for index in range(count):
            graded, row = lab_grade(images[index], masks[index], references[index], reference_masks[index],
                                    apply_to=apply_to, **settings)
            results.append(graded)
            rows.append({"index": index, **row})
            if index < PREVIEW_LIMIT:
                delta = [after - before for before, after in zip(row["target"]["lab_mean"], row["result"]["lab_mean"])]
                title = (f"Image {index + 1} | Lab mean {_triple(row['target']['lab_mean'])} -> "
                         f"{_triple(row['result']['lab_mean'])} (reference {_triple(row['reference']['lab_mean'])}) "
                         f"| shift {_triple(delta, signed=True)} | stretch {_triple(row['stretch'])}")
                if row["clipped_pixels"]:
                    title += f" | {row['clipped_pixels']} px clipped to sRGB"
                nodes.append(compare_entry(images[index], graded, index, title, debug=mask_preview(masks[index])))
        receipt = {"schema": SCHEMA, "color_space": "CIE Lab, D65 2-degree white, decoded sRGB; alpha unchanged",
                   "method": "per channel (lab - mean) * stretch + reference mean, blended by weight * amount",
                   "apply_to": apply_to, **settings, "image_count": count, "images": rows}
        return texture_result(results, receipt, nodes, safe_send_sync, "maskedlabgrade", kwargs.get("node_id"))


def _triple(values, signed=False):
    return "[" + ", ".join(f"{value:+.1f}" if signed else f"{value:.1f}" for value in values) + "]"


NODE_CLASS_MAPPINGS = {"LF_MaskedLabGrade": LF_MaskedLabGrade}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_MaskedLabGrade": "Masked Lab grade"}
