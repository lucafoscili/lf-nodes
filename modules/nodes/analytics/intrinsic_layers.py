"""Albedo, diffuse shading and residual of one image, estimated by a published intrinsic decomposition model."""
import numpy as np
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.torch.intrinsic_layers import available_releases, decompose, to_display
from ...utils.helpers.ui import create_cached_compare_node
from ...utils.image_regions import single_image


def _image(array):
    return torch.from_numpy(np.ascontiguousarray(array, dtype=np.float32))[None]


class LF_IntrinsicLayers:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Exactly one display-referred (sRGB) image."}),
                "release": (available_releases(), {"tooltip": "Weights folder content under models/intrinsic: a release's stage_0..stage_4 files."}),
                "resize_conf": (Input.FLOAT, {"default": 0.0, "min": -1.0, "max": 1.0, "step": 0.05, "tooltip": "The pipeline's resizing confidence (0 is the authors' R_0); -1 keeps the source size."}),
                "base_size": (Input.INTEGER, {"default": 384, "min": 128, "max": 1024, "step": 32, "tooltip": "Base resolution of the global estimates."}),
            },
            "optional": {"ui_widget": (Input.LF_COMPARE, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE, Input.JSON, Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ("albedo", "diffuse_shading", "residual", "report", "albedo_display", "shading_display")
    OUTPUT_IS_LIST = (False, False, False, False, False, False)
    OUTPUT_TOOLTIPS = (
        "Linear albedo at the source size.",
        "Linear diffuse shading in colour at the source size; may exceed 1.",
        "Linear residual, image minus albedo times shading: sheen and emitters positive, clipped pixels negative.",
        "lf.intrinsic-layers.v1: release, working size and each layer's mean, minimum and maximum.",
        "Albedo encoded for display (sRGB).",
        "Diffuse shading encoded for display, halved so lights up to 2 stay visible.",
    )

    def on_exec(self, image=None, release=None, resize_conf=0.0, base_size=384, **kwargs):
        source = single_image(image, "image")
        if release in (None, "none found"):
            raise ValueError("no intrinsic release found under models/intrinsic (stage_0..stage_4 .pt files).")
        conf = float(resize_conf)
        layers, report = decompose(source, release, resize_conf=None if conf < 0 else conf, base_size=int(base_size))
        albedo_display = _image(np.clip(to_display(layers["albedo"]), 0, 1))
        shading_display = _image(np.clip(to_display(layers["diffuse_shading"] / 2), 0, 1))
        residual_display = _image(np.clip(to_display(np.clip(layers["residual"], 0, None)), 0, 1))
        nodes = [create_cached_compare_node(source, albedo_display, index=0, title="image / albedo"),
                 create_cached_compare_node(albedo_display, shading_display, index=1, title="albedo / diffuse shading (x0.5)"),
                 create_cached_compare_node(source, residual_display, index=2, title="image / positive residual")]
        payload = {"dataset": {"nodes": nodes}, "report": report}
        safe_send_sync("intrinsiclayers", payload, kwargs.get("node_id"))
        first = lambda array: normalize_output_image([_image(array)])[0][0]
        return {"ui": {"lf_output": [payload]},
                "result": (first(layers["albedo"]), first(layers["diffuse_shading"]), first(layers["residual"]),
                           report, normalize_output_image([albedo_display])[0][0],
                           normalize_output_image([shading_display])[0][0])}


NODE_CLASS_MAPPINGS = {"LF_IntrinsicLayers": LF_IntrinsicLayers}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_IntrinsicLayers": "Intrinsic layers"}
