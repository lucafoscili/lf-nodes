"""How much of the change between two registered renders a colour grade explains, and what is left."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.tone import as_rgb, grade_split
from ...utils.helpers.ui import create_cached_compare_node
from ...utils.image_regions import single_image


class LF_GradeSplit:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "before": (Input.IMAGE, {"tooltip": "Exactly one render: the scene before the change."}),
                "after": (Input.IMAGE, {"tooltip": "Exactly one registered render of the same scene after it, same size."}),
                "lut_size": (Input.INTEGER, {"default": 32, "min": 2, "max": 64, "tooltip": "Cells per channel of the whole-frame colour lookup."}),
                "local_size": (Input.INTEGER, {"default": 16, "min": 2, "max": 32, "tooltip": "Cells per channel, and of neighbourhood luma, of the local lookup."}),
                "local_sigma": (Input.FLOAT, {"default": 1 / 60, "min": 0.001, "max": 0.5, "step": 0.001, "tooltip": "Neighbourhood blur as a share of the width."}),
                "fine_sigma": (Input.FLOAT, {"default": 2.0, "min": 0.5, "max": 64.0, "step": 0.5, "tooltip": "Blur in pixels separating fine from mid detail."}),
                "coarse_sigma": (Input.FLOAT, {"default": 16.0, "min": 1.0, "max": 256.0, "step": 1.0, "tooltip": "Blur in pixels separating mid detail from coarse light."}),
            },
            "optional": {"ui_widget": (Input.LF_COMPARE, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.JSON, Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ("report", "change", "left")
    OUTPUT_IS_LIST = (False, False, False)
    OUTPUT_TOOLTIPS = (
        "lf.grade-split.v1: shares explained by one colour lookup and by a neighbourhood-keyed one, spatial bands of the change and of what is left, tone curve and saturation per band.",
        "The change in luma, after minus before: grey none, red brighter, blue darker, full at a quarter.",
        "What the local lookup leaves, in the same colours: the part only geometry, light and materials explain.",
    )

    def on_exec(self, before=None, after=None, lut_size=32, local_size=16, local_sigma=1 / 60, fine_sigma=2.0,
                coarse_sigma=16.0, **kwargs):
        before_image, after_image = single_image(before, "before"), single_image(after, "after")
        report, change, left = grade_split(
            as_rgb(before_image, "before"), as_rgb(after_image, "after"), lut_size=int(lut_size),
            local_size=int(local_size), local_sigma=float(local_sigma), fine_sigma=float(fine_sigma),
            coarse_sigma=float(coarse_sigma))
        explained = report["explained"]
        title = (f"grade {100 * explained['grade']:.1f}% | +local {100 * explained['local_adds']:.1f}% | "
                 f"left coarse {100 * report['left_bands']['coarse']:.0f}%")
        dataset = {"nodes": [
            create_cached_compare_node(before_image, after_image, index=0, title="before / after"),
            create_cached_compare_node(change, left, index=1, title=f"change / left | {title}"),
        ]}
        payload = {"dataset": dataset, "report": report}
        safe_send_sync("gradesplit", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]},
                "result": (report, normalize_output_image([change])[0][0], normalize_output_image([left])[0][0])}


NODE_CLASS_MAPPINGS = {"LF_GradeSplit": LF_GradeSplit}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_GradeSplit": "Grade split"}
