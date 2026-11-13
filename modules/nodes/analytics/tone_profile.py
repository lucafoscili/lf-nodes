"""Tone profiles of a render's regions, and their tone curve against another render's (unregistered shots)."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_json_input
from ...utils.helpers.tone import as_rgb, one_image, tone_profile
from ...utils.helpers.tone.region_reads import PROFILE_SCHEMA, region_dict
from ...utils.image_regions import single_value


def _curve(profile, reference):
    if 'mean' not in profile or 'mean' not in (reference or {}):
        return None
    return {'deciles': [[a, b] for a, b in zip(reference['deciles'], profile['deciles'])],
            'saturation_thirds': [[a, b] for a, b in zip(reference['saturation_thirds'], profile['saturation_thirds'])],
            'mean_ratio': profile['mean'] / reference['mean'] if reference['mean'] > 0 else None,
            'shade_ratio': profile['shade'] / reference['shade'] if reference['shade'] > 0 else None}


class LF_ToneProfile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Exactly one display-referred image."}),
                "min_pixels": (Input.INTEGER, {"default": 200, "min": 1, "max": 1_000_000, "tooltip": "Regions with fewer pixels report a warning instead of numbers."}),
            },
            "optional": {
                "masks": (Input.MASK, {"tooltip": "One region set at the image's size (lf.text-region-masks.v1 order)."}),
                "metadata": (Input.JSON, {"tooltip": "The region set's lf.text-region-masks.v1 document."}),
                "reference": (Input.JSON, {"tooltip": "Another image's lf.tone-profile.v1 report: each shared region gains its tone curve against it."}),
                "ui_widget": (Input.LF_TREE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.JSON,)
    RETURN_NAMES = ("profile",)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ("lf.tone-profile.v1: per region (and the whole frame) luma mean, median, deciles, shade, fill, warmth, sheen, detail and saturation by third; with a reference, each region's decile curve against it.",)

    def on_exec(self, image=None, min_pixels=200, masks=None, metadata=None, reference=None, **kwargs):
        source = one_image(image, "image")
        rgb = as_rgb(source, "image")
        regions = {"frame": None}
        if masks is not None or metadata is not None:
            if masks is None or metadata is None:
                raise ValueError("masks and metadata come together.")
            regions.update(region_dict(masks, metadata, rgb.shape[:2], "masks"))
        profiles = {name: tone_profile(rgb, mask, min_pixels=int(min_pixels)) for name, mask in regions.items()}
        report = {"schema": PROFILE_SCHEMA, "size": [rgb.shape[1], rgb.shape[0]], "regions": profiles}
        if reference is not None:
            reference = normalize_json_input(single_value(reference, "reference"))
            if not isinstance(reference, dict) or reference.get("schema") != PROFILE_SCHEMA:
                raise ValueError("reference must be an lf.tone-profile.v1 report.")
            report["against_reference"] = {name: _curve(profile, reference["regions"].get(name))
                                           for name, profile in profiles.items() if name in reference["regions"]}
        against = report.get("against_reference") or {}
        nodes = [_tree_node(index, name, profile, against.get(name))
                 for index, (name, profile) in enumerate(profiles.items())]
        # The report travels on the socket; the UI carries only the tree, which shows each of its values. A Runner
        # manifest walks every node's UI output under one item budget, so a graph of several profiles stays inside it.
        payload = {"dataset": {"nodes": nodes}}
        safe_send_sync("toneprofile", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (report,)}


def _number(value, digits):
    """A label value; None where the profile has none (a black region's ratios)."""
    return "n/a" if value is None else f"{value:.{digits}f}"


def _numbers(values, digits=3):
    return " ".join(_number(value, digits) for value in values)


def _tree_node(index, name, profile, curve):
    """One region: its headline, then a few lines holding every value of its profile."""
    if "mean" not in profile:
        return {"id": str(index), "value": f"{name}: N/A | {profile['warning']}"}
    lines = [
        f"pixels {profile['n']} | mean {_number(profile['mean'], 3)} | median {_number(profile['median'], 3)}",
        f"shade {_number(profile['shade'], 3)} | fill {_number(profile['fill'], 3)} | shade R/B "
        f"{_number(profile['shade_rb'], 2)} | R/B {_number(profile['rb'], 2)}",
        f"sheen {_number(profile['sheen'], 3)} | detail {_number(profile['detail'], 2)} | saturation "
        f"{_number(profile['saturation'], 3)} | by third {_numbers(profile['saturation_thirds'])}",
        f"deciles {_numbers(profile['deciles'])}",
    ]
    if curve:
        lines.append(f"against reference: mean x{_number(curve['mean_ratio'], 3)} | shade x"
                     f"{_number(curve['shade_ratio'], 3)} | deciles from {_numbers(row[0] for row in curve['deciles'])}")
    return {"id": str(index), "value": (f"{name}: mean {_number(profile['mean'], 3)} | shade "
                                        f"{_number(profile['shade'], 3)} | fill {_number(profile['fill'], 3)} | R/B "
                                        f"{_number(profile['rb'], 2)} | sat {_number(profile['saturation'], 2)}"),
            "children": [{"id": f"{index}_{line_index}", "value": line} for line_index, line in enumerate(lines)]}


NODE_CLASS_MAPPINGS = {"LF_ToneProfile": LF_ToneProfile}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_ToneProfile": "Tone profile"}
