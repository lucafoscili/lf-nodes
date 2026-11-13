"""Where a change of light lands between two registered renders: the per-pixel luma ratio and its band medians."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.tone import DEFAULT_EDGES, as_rgb, luma_ratio_map
from ...utils.helpers.tone.common import binary_masks
from ...utils.helpers.ui import create_cached_compare_node
from ...utils.image_regions import single_image


class LF_LumaRatioMap:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "before": (Input.IMAGE, {"tooltip": "Exactly one render: the scene before the change."}),
                "after": (Input.IMAGE, {"tooltip": "Exactly one registered render of the same scene after it, same size."}),
                "sigma": (Input.FLOAT, {"default": 3.0, "min": 0.0, "max": 64.0, "step": 0.5, "tooltip": "Blur in pixels before the ratio, so texture does not read as light."}),
                "floor": (Input.FLOAT, {"default": 0.03, "min": 0.001, "max": 0.5, "step": 0.001, "tooltip": "Before luma under which a pixel is left out."}),
                "band_edges": (Input.STRING, {"default": ",".join(f"{edge:g}" for edge in DEFAULT_EDGES), "tooltip": "Comma-separated, increasing before-luma band edges."}),
                "stops": (Input.FLOAT, {"default": 1.0, "min": 0.1, "max": 8.0, "step": 0.1, "tooltip": "Stops at which the picture's colour is full."}),
            },
            "optional": {
                "mask": (Input.MASK, {"tooltip": "One mask at the images' size: each band reports outside and inside it."}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.JSON, Input.IMAGE)
    RETURN_NAMES = ("report", "ratio_map")
    OUTPUT_IS_LIST = (False, False)
    OUTPUT_TOOLTIPS = (
        "lf.luma-ratio-map.v1: the after/before luma ratio's median per band of before luma, outside and inside the mask.",
        "Grey unchanged, orange brighter, blue darker (full at the chosen stops), black left out.",
    )

    def on_exec(self, before=None, after=None, sigma=3.0, floor=0.03, band_edges="", stops=1.0, mask=None, **kwargs):
        before_image, after_image = single_image(before, "before"), single_image(after, "after")
        inside = None
        if mask is not None:
            inside = binary_masks(mask)
            if inside.ndim == 3:
                if inside.shape[0] != 1:
                    raise ValueError(f"mask must be one mask, not a batch of {inside.shape[0]}.")
                inside = inside[0]
        report, picture = luma_ratio_map(
            as_rgb(before_image, "before"), as_rgb(after_image, "after"), mask=inside, sigma=float(sigma),
            floor=float(floor), edges=band_edges or DEFAULT_EDGES, stops=float(stops))
        darkest, brightest = report["darkest"], report["brightest"]
        title = "ratio map"
        if darkest is not None:
            title += f" | darkest band x{darkest:.2f} | brightest x{brightest:.2f}"
        dataset = {"nodes": [create_cached_compare_node(after_image, picture, index=0, title=title)]}
        payload = {"dataset": dataset, "report": report}
        safe_send_sync("lumaratiomap", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (report, normalize_output_image([picture])[0][0])}


NODE_CLASS_MAPPINGS = {"LF_LumaRatioMap": LF_LumaRatioMap}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_LumaRatioMap": "Luma ratio map"}
