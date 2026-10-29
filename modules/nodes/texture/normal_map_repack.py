"""Normal map check and repack: validate a tangent normal map, renormalise it, convert its green convention."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.torch.texture_maps import (
    NORMAL_DISC_SLACK, NORMAL_GREEN, NORMAL_LAYOUTS, NORMAL_UNIT_TOLERANCE, NORMAL_VANISHING_LENGTH, NORMAL_Z_MODES,
    normal_map_repack,
)
from ...utils.texture_nodes import (
    PREVIEW_LIMIT, compare_entry, mask_preview, optional_masks, scalar, texture_images, texture_result,
)

SCHEMA = "lf.normal-map-repack.v1"


class LF_NormalMapRepack:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Tangent-space normal map(s), stored values (not colour-managed)."}),
                "layout": (list(NORMAL_LAYOUTS), {"default": "xyz_rgb",
                                                  "tooltip": "xyz_rgb: X red, Y green, Z blue. xy_ag: X alpha, Y green, no Z (swizzled two-channel maps)."}),
                "green_in": (list(NORMAL_GREEN), {"default": "opengl",
                                                  "tooltip": "The map's green convention: opengl (Y up the image) or directx (Y down)."}),
                "green_out": (list(NORMAL_GREEN), {"default": "opengl",
                                                   "tooltip": "The convention to write; green is flipped when it differs from green_in."}),
                "z_mode": (list(NORMAL_Z_MODES), {"default": "rebuild_z",
                                                  "tooltip": "rebuild_z: keep X,Y and rebuild Z on the forward hemisphere. normalize_xyz: scale the stored vector to unit length, keeping Z's sign."}),
                "max_invalid_share": (Input.FLOAT, {"default": 0.01, "min": 0.0, "max": 1.0, "step": 0.005,
                                                    "tooltip": "Largest share of checked pixels that may be invalid; above it the node raises."}),
            },
            "optional": {
                "mask": (Input.MASK, {"tooltip": "Pixels to validate (above 0.5), such as UV coverage. Defaults to all; every pixel is repacked."}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Check that an image is a tangent normal map in the stated layout, renormalise it, flip green "
                   "between OpenGL and DirectX, rebuild Z, and report what was found. Raises past the invalid limit.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False, True)
    RETURN_NAMES = ("image", "report", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.IMAGE)
    OUTPUT_TOOLTIPS = (
        "Repacked normal map batch: unit vectors as RGB in green_out's convention (alpha kept for xyz_rgb).",
        "lf.normal-map-repack.v1: shares of invalid, out-of-disc, facing-away, vanishing and renormalised pixels.",
        "The same normal maps as an authoritative list.",
    )

    def on_exec(self, image=None, mask=None, **kwargs):
        images = texture_images(image, "image")
        count = len(images)
        masks = optional_masks(mask, count, "mask")
        settings = {name: scalar(kwargs.get(name), name) for name in ("layout", "green_in", "green_out", "z_mode")}
        max_invalid_share = float(scalar(kwargs.get("max_invalid_share"), "max_invalid_share"))
        if not 0 <= max_invalid_share <= 1:
            raise ValueError("max_invalid_share must lie in 0..1.")
        results, rows, nodes = [], [], []
        for index, item in enumerate(images):
            repacked, row = normal_map_repack(item, masks[index], max_invalid_share=max_invalid_share, **settings)
            results.append(repacked)
            rows.append({"index": index, **row})
            if index < PREVIEW_LIMIT:
                title = (f"Image {index + 1} | invalid {row['invalid_share']:.2%} | renormalised "
                         f"{row['renormalized_share']:.2%} | mean length {row['stored_length']['mean']:.3f}"
                         f" | green {row['green_in']} -> {row['green_out']}")
                before = item if settings["layout"] == "xyz_rgb" else item[..., [3, 1, 2]]
                nodes.append(compare_entry(before, repacked, index, title,
                                           debug=mask_preview(masks[index]) if masks[index] is not None else None))
        receipt = {"schema": SCHEMA, "decode": "value * 2 - 1", "mask_membership": "value > 0.5",
                   "disc_slack": NORMAL_DISC_SLACK, "vanishing_length": NORMAL_VANISHING_LENGTH,
                   "unit_tolerance": NORMAL_UNIT_TOLERANCE, **settings, "max_invalid_share": max_invalid_share,
                   "image_count": count, "images": rows}
        return texture_result(results, receipt, nodes, safe_send_sync, "normalmaprepack", kwargs.get("node_id"))


NODE_CLASS_MAPPINGS = {"LF_NormalMapRepack": LF_NormalMapRepack}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_NormalMapRepack": "Normal map check and repack"}
