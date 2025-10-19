import json
import torch

from dataclasses import replace

from server import PromptServer

from . import CATEGORY
from ...utils.constants import (
    EVENT_PREFIX,
    FUNCTION,
    Input,
    OPTIONAL_VECTOR_MODE_COMBO,
    SIZE_MODE_COMBO,
    TRACE_PRESET_COMBO
)
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath
from ...utils.helpers.conversion import (
    SVGTraceConfig,
    numpy_to_tensor,
    numpy_to_svg,
    tensor_to_numpy,
    tensor_to_pil,
)
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.ui import create_compare_node

PRESET_CONFIGS: dict[str, SVGTraceConfig] = {
    "max_quality": SVGTraceConfig(
        num_colors=8,
        simplify_tol=0.01,
        vector_mode="fill",
        stroke_width=0.0,
        upsample_scale=6,
        mask_blur=1.0,
        mask_offset=0,
        mask_close_iters=2,
        mask_open_iters=0,
        smooth_passes=1,
        min_area_ratio=0.00002,
        pre_blur_sigma=0.15,
        bilateral_d=5,
        bilateral_sigma_color=20.0,
        bilateral_sigma_space=20.0,
        collinear_angle_tol=3.0,
        engine="vtracer",
        vtracer_mode="spline",
        vtracer_hierarchical="stacked",
        vtracer_filter_speckle=3,
        vtracer_color_precision=6,
        vtracer_layer_difference=10,
        vtracer_corner_threshold=80,
        vtracer_length_threshold=3.5,
        vtracer_max_iterations=12,
        vtracer_splice_threshold=50,
        vtracer_path_precision=3,
    ),
    "high_quality": SVGTraceConfig(
        num_colors=6,
        simplify_tol=0.014,
        vector_mode="fill",
        stroke_width=0.0,
        upsample_scale=5,
        mask_blur=0.9,
        mask_offset=0,
        mask_close_iters=2,
        mask_open_iters=0,
        smooth_passes=1,
        min_area_ratio=0.00002,
        pre_blur_sigma=0.18,
        bilateral_d=6,
        bilateral_sigma_color=30.0,
        bilateral_sigma_space=30.0,
        collinear_angle_tol=4.0,
        engine="vtracer",
        vtracer_mode="spline",
        vtracer_hierarchical="stacked",
        vtracer_filter_speckle=4,
        vtracer_color_precision=6,
        vtracer_layer_difference=12,
        vtracer_corner_threshold=85,
        vtracer_length_threshold=4.0,
        vtracer_max_iterations=12,
        vtracer_splice_threshold=55,
        vtracer_path_precision=3,
    ),
    "balanced": SVGTraceConfig(
        num_colors=5,
        simplify_tol=0.012,
        vector_mode="fill",
        stroke_width=0.0,
        upsample_scale=3,
        mask_blur=0.9,
        mask_offset=0,
        mask_close_iters=1,
        mask_open_iters=0,
        smooth_passes=1,
        min_area_ratio=0.00002,
        pre_blur_sigma=0.15,
        bilateral_d=5,
        bilateral_sigma_color=28.0,
        bilateral_sigma_space=28.0,
        collinear_angle_tol=4.0,
        engine="vtracer",
        vtracer_mode="spline",
        vtracer_hierarchical="stacked",
        vtracer_filter_speckle=5,
        vtracer_color_precision=6,
        vtracer_layer_difference=10,
        vtracer_corner_threshold=85,
        vtracer_length_threshold=4.0,
        vtracer_max_iterations=10,
        vtracer_splice_threshold=55,
        vtracer_path_precision=3,
    ),
    "max_speed": SVGTraceConfig(
        num_colors=4,
        simplify_tol=0.02,
        vector_mode="fill",
        stroke_width=0.0,
        upsample_scale=2,
        mask_blur=0.6,
        mask_offset=0,
        mask_close_iters=1,
        mask_open_iters=0,
        smooth_passes=1,
        min_area_ratio=0.00002,
        pre_blur_sigma=0.1,
        bilateral_d=0,
        bilateral_sigma_color=0.0,
        bilateral_sigma_space=0.0,
        collinear_angle_tol=5.0,
        engine="contour",
        vtracer_mode="spline",
        vtracer_hierarchical="stacked",
        vtracer_filter_speckle=3,
        vtracer_color_precision=6,
        vtracer_layer_difference=8,
        vtracer_corner_threshold=80,
        vtracer_length_threshold=3.5,
        vtracer_max_iterations=8,
        vtracer_splice_threshold=45,
        vtracer_path_precision=3,
    ),
    "custom": SVGTraceConfig(),
}


# region LF_ImageToSVG
class LF_ImageToSVG:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor to vectorize"
                }),
                "preset": (TRACE_PRESET_COMBO, {
                    "default": "max_quality",
                    "tooltip": "Choose a quality/speed profile. Max quality favours fidelity, max speed favours performance."
                }),
            },
            "optional": {
                "advanced_config": (Input.JSON, {
                    "default": {},
                    "tooltip": "Optional overrides for preset values (keys map to SVGTraceConfig fields)."
                }),
                "render_mode": (OPTIONAL_VECTOR_MODE_COMBO, {
                    "default": "preset",
                    "tooltip": "Override preset stroke/fill behaviour."
                }),
                "fill_color": (Input.STRING, {
                    "default": "",
                    "tooltip": "Override fill colour (hex or CSS). Leave blank to use preset colours."
                }),
                "stroke_color": (Input.STRING, {
                    "default": "",
                    "tooltip": "Override stroke colour (hex or CSS). Leave blank to use preset colours."
                }),
                "background_color": (Input.STRING, {
                    "default": "",
                    "tooltip": "Background colour for the SVG canvas. Leave blank for transparent."
                }),
                "stroke_width": (Input.FLOAT, {
                    "default": 0.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Stroke width when stroke rendering is enabled. Leave at 0 to keep preset."
                }),
                "size_mode": (SIZE_MODE_COMBO, {
                    "default": "preset",
                    "tooltip": "Responsive outputs use width/height 100%%, fixed uses pixel dimensions."
                }),
                "viewbox": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional viewBox override in the format: 'minX minY width height' (e.g. '0 0 24 24'). Leave blank to keep the original image dimensions."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True, False, True)
    OUTPUT_TOOLTIPS = (
        "Generated SVG string.",
        "List of generated SVG strings.",
        "Original image tensor.",
        "List of original image tensors.",
        "Palette used for the SVG.",
        "List of palettes used for the SVG."
    )
    RETURN_NAMES = ("svg", "svg_list", "image", "image_list", "palette", "palette_list")
    RETURN_TYPES = (Input.STRING, Input.STRING, Input.IMAGE, Input.IMAGE, Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        self._temp_cache.cleanup()

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        preset: str = (normalize_list_to_value(kwargs.get("preset")) or "max_quality").lower()
        advanced_cfg = normalize_list_to_value(kwargs.get("advanced_config")) or {}

        if isinstance(advanced_cfg, str):
            try:
                parsed = json.loads(advanced_cfg)
                advanced_cfg = parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                advanced_cfg = {}
        elif not isinstance(advanced_cfg, dict):
            advanced_cfg = {}

        base_config = PRESET_CONFIGS.get(preset, PRESET_CONFIGS["max_quality"])
        config = replace(base_config)

        for key, value in advanced_cfg.items():
            if value is None or not hasattr(config, key):
                continue
            setattr(config, key, value)

        render_mode = normalize_list_to_value(kwargs.get("render_mode"))
        if isinstance(render_mode, str) and render_mode and render_mode.lower() != "preset":
            config.vector_mode = render_mode.lower()

        fill_color = normalize_list_to_value(kwargs.get("fill_color"))
        if isinstance(fill_color, str):
            fill_color = fill_color.strip()
            config.fill_color_override = fill_color or config.fill_color_override

        stroke_color = normalize_list_to_value(kwargs.get("stroke_color"))
        if isinstance(stroke_color, str):
            stroke_color = stroke_color.strip()
            config.stroke_color_override = stroke_color or config.stroke_color_override

        background_color = normalize_list_to_value(kwargs.get("background_color"))
        if isinstance(background_color, str):
            background_color = background_color.strip()
            config.background_color = background_color or config.background_color

        stroke_width_override = normalize_list_to_value(kwargs.get("stroke_width"))
        if isinstance(stroke_width_override, (int, float)) and stroke_width_override > 0:
            config.stroke_width = float(stroke_width_override)

        size_mode = normalize_list_to_value(kwargs.get("size_mode"))
        if isinstance(size_mode, str) and size_mode and size_mode.lower() != "preset":
            config.size_mode = size_mode.lower()

        viewbox_override = normalize_list_to_value(kwargs.get("viewbox"))
        if isinstance(viewbox_override, str):
            viewbox_override = viewbox_override.strip()
            if viewbox_override:
                config.viewbox_override = viewbox_override

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        previews: list[torch.Tensor] = []
        svgs: list[str] = []
        palettes: list[list[str]] = []

        for index, img in enumerate(image):
            arr = tensor_to_numpy(img)
            svg_str, proc, palette = numpy_to_svg(arr, config)
            preview = numpy_to_tensor(proc)

            pil_image_original = tensor_to_pil(img)
            output_file_s, subfolder_s, filename_s = resolve_filepath(
                filename_prefix="svg_s",
                image=img,
                temp_cache=self._temp_cache
            )
            pil_image_original.save(output_file_s, format="PNG")
            filename_s = get_resource_url(subfolder_s, filename_s, "temp")

            pil_image_blended = tensor_to_pil(preview)
            output_file_t, subfolder_t, filename_t = resolve_filepath(
                filename_prefix="svg_t",
                image=preview,
                temp_cache=self._temp_cache
            )
            pil_image_blended.save(output_file_t, format="PNG")
            filename_t = get_resource_url(subfolder_t, filename_t, "temp")

            previews.append(preview)
            svgs.append(svg_str)
            palettes.append(palette)
            nodes.append(create_compare_node(filename_s, filename_t, index))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imagetosvg", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        image_batch, image_list = normalize_output_image(previews)

        return (svgs[0], svgs, image_batch[0], image_list, palettes[0], palettes)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImageToSVG": LF_ImageToSVG,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageToSVG": "Image to SVG",
}
# endregion
