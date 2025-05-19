import torch

from server import PromptServer

from ..utils.constants import CATEGORY_PREFIX, EVENT_PREFIX, FUNCTION, Input
from ..utils.filters import blend_effect, bloom_effect, brightness_effect, clarity_effect, contrast_effect, desaturate_effect, film_grain_effect, gaussian_blur_effect, line_effect, saturation_effect, sepia_effect, split_tone_effect, tilt_shift_effect, vibrance_effect, vignette_effect
from ..utils.helpers import normalize_input_image, normalize_list_to_value, normalize_output_image, process_and_save_image

CATEGORY = f"{CATEGORY_PREFIX}/Filters"

# region LF_Blend
class LF_Blend:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "The base image to blend with."
                }),
                "overlay_image": (Input.IMAGE, {
                    "tooltip": "The overlay image to blend onto the base image."
                }),
                "opacity": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01, 
                    "tooltip": "Opacity of the overlay. 0 means invisible, 1 means fully opaque."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        overlay_image: list[torch.Tensor] = normalize_input_image(kwargs.get("overlay_image"))
        opacity: float = normalize_list_to_value(kwargs.get("opacity"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=blend_effect,
            filter_args={
                'overlay_image': overlay_image[0],
                'alpha_mask': opacity,
            },
            filename_prefix="blend",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}blend", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Bloom
class LF_Bloom:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": (
                        "Source frame to receive the glow.\n"
                        "Tip ▸ Works best if the image is already at final resolution; "
                        "up-res after blooming can soften the effect."
                    )
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.80,
                    "min": 0.00,
                    "max": 1.00,
                    "step": 0.01,
                    "tooltip": (
                        "Bright-pass cutoff.\n"
                        "‣ 0 = everything glows • 1 = nothing glows\n"
                        "‣ For dim scenes start around **0.15-0.35**; for high-key images **0.65-0.85**.\n"
                        "Accepts 0-1 *or* 0-255 (e.g. 200 ≈ 0.78)."
                    )
                }),
                "radius": (Input.INTEGER, {
                    "default": 15,
                    "min": 3,
                    "max": 127,
                    "step": 2,
                    "tooltip": (
                        "Blur radius in **pixels** (odd numbers only).\n"
                        "Bigger radius → softer, more cinematic glow.\n"
                        "A value ~1-2 % of image width is a good starting point."
                    )
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.60,
                    "min": 0.00,
                    "max": 2.00,
                    "step": 0.05,
                    "tooltip": (
                        "How strong the bloom reads after compositing.\n"
                        "1.0 = add the blurred highlights at full strength.\n"
                        "< 1.0 softens; > 1.0 exaggerates (can wash out mid-tones)."
                    )
                }),
            },
            "optional": {
                "tint": (Input.STRING, {
                    "default": "FFFFFF",
                    "tooltip": (
                        "Hex colour for the glow (e.g. FFCCAA).\n"
                        "Pure white **FFFFFF** keeps original hue."
                    )
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }


    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        threshold: float = normalize_list_to_value(kwargs.get("threshold"))
        radius: int = normalize_list_to_value(kwargs.get("radius"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        tint: str = normalize_list_to_value(kwargs.get("tint", "FFFFFF"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=bloom_effect,
            filter_args={
                'threshold': threshold,
                'radius': radius,
                'intensity': intensity,
                'tint': tint
            },
            filename_prefix="bloom",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}bloom", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Brightness
class LF_Brightness:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "brightness_strength": (Input.FLOAT, {
                    "default": 0.0, 
                    "min": -1.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Adjust the brightness of the image. Negative values darken, positive values brighten."
                }),
                "gamma": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": 0.1, 
                    "max": 3.0, 
                    "step": 0.1, 
                    "tooltip": "Adjust the gamma correction. Values < 1 brighten shadows, > 1 darken highlights."
                }),
            },
            "optional": {
                "midpoint": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Defines the tonal midpoint for brightness scaling."
                }),
                "localized_brightness": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Enhance brightness locally in darker regions."
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        brightness_strength: float = normalize_list_to_value(kwargs.get("brightness_strength"))
        gamma: float = normalize_list_to_value(kwargs.get("gamma"))
        midpoint: float = normalize_list_to_value(kwargs.get("midpoint", 0.5))
        localized_brightness: bool = kwargs.get("localized_brightness", False)

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=brightness_effect,
            filter_args={
                'brightness_strength': brightness_strength,
                'gamma': gamma,
                'midpoint': midpoint,
                'localized_brightness': localized_brightness,
            },
            filename_prefix="brightness",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}brightness", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Clarity
class LF_Clarity:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "clarity_strength": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1, 
                    "tooltip": "Controls the amount of contrast enhancement in midtones."
                }),
                "sharpen_amount": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1, 
                    "tooltip": "Controls how much sharpening is applied to the image."
                }),
                "blur_kernel_size": (Input.INTEGER, {
                    "default": 7, 
                    "min": 1, 
                    "max": 15, 
                    "step": 2, 
                    "tooltip": "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        clarity_strength: float = normalize_list_to_value(kwargs.get("clarity_strength"))
        sharpen_amount: float = normalize_list_to_value(kwargs.get("sharpen_amount"))
        blur_kernel_size: int = normalize_list_to_value(kwargs.get("blur_kernel_size"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=clarity_effect,
            filter_args={
                'clarity_strength': clarity_strength,
                'sharpen_amount': sharpen_amount,
                'blur_kernel_size': blur_kernel_size,
            },
            filename_prefix="clarity",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}clarity", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Contrast
class LF_Contrast:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "contrast_strength": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": -1.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Controls the intensity of the contrast adjustment. 1.0 is no change, below 1 reduces contrast, above 1 increases contrast."
                }),
                "midpoint": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Defines the tonal midpoint for contrast scaling."
                }),
            },
            "optional": {
                "localized_contrast": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Apply contrast enhancement locally to edges and textures."
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict) -> None:
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        contrast_strength: float = normalize_list_to_value(kwargs.get("contrast_strength"))
        midpoint: float = normalize_list_to_value(kwargs.get("midpoint"))
        localized_contrast: bool = kwargs.get("localized_contrast", False)

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=contrast_effect,
            filter_args={
                'contrast_strength': contrast_strength,
                'midpoint': midpoint,
                'localized_contrast': localized_contrast,
            },
            filename_prefix="contrast",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}contrast", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Desaturation
class LF_Desaturation:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "global_level": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Controls the total intensity of the desaturation. 0 is no effect, 1 is fully desaturated."
                }),
                "r_channel": (Input.FLOAT, {
                    "default": 1, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Controls the intensity of the red channel desaturation relative to the total strength of the filter."
                }),
                "g_channel": (Input.FLOAT, {
                    "default": 1, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Controls the intensity of the green channel desaturation relative to the total strength of the filter."
                }),
                "b_channel": (Input.FLOAT, {
                    "default": 1, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "Controls the intensity of the blue channel desaturation relative to the total strength of the filter."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        global_level: float = normalize_list_to_value(kwargs.get("global_level"))
        r: float = normalize_list_to_value(kwargs.get("r_channel", 1))
        g: float = normalize_list_to_value(kwargs.get("g_channel", 1))
        b: float = normalize_list_to_value(kwargs.get("b_channel", 1))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=desaturate_effect,
            filter_args={
                'global_level': global_level,
                'channel_levels': [r, g, b],
            },
            filename_prefix="desaturation",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}desaturation", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_FilmGrain
class LF_FilmGrain:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the strength of the film grain effect."
                }),
                "size": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.5,
                    "max": 5.0,
                    "step": 0.1,
                    "tooltip": "Controls the size of the grain. Smaller values = finer grain."
                }),
                "tint": (Input.STRING, {
                    "default": "FFFFFF", 
                    "tooltip": "Hexadecimal color (default is FFFFFF for no tint)."
                }),
                "soft_blend": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "If True, uses a soft blending mode for the grain."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        size: float = normalize_list_to_value(kwargs.get("size"))
        tint: str = normalize_list_to_value(kwargs.get("tint", "FFFFFF"))
        soft_blend: bool = normalize_list_to_value(kwargs.get("soft_blend", False))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=film_grain_effect,
            filter_args={
                "intensity": intensity,
                "size": size,
                "tint": tint,
                "soft_blend": soft_blend
            },
            filename_prefix="film_grain",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}filmgrain", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_GaussianBlur
class LF_GaussianBlur:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "blur_kernel_size": (Input.INTEGER, {
                    "default": 7, 
                    "min": 1, 
                    "max": 51, 
                    "step": 2, 
                    "tooltip": "Controls the size of the Gaussian blur kernel. Higher values mean more smoothing."
                }),
                "blur_sigma": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 10.0, 
                    "step": 0.1, 
                    "tooltip": "Standard deviation for the Gaussian kernel. Controls blur intensity."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        blur_kernel_size: int = normalize_list_to_value(kwargs.get("blur_kernel_size"))
        blur_sigma: float = normalize_list_to_value(kwargs.get("blur_sigma"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=gaussian_blur_effect,
            filter_args={
                'blur_kernel_size': blur_kernel_size,
                'blur_sigma': blur_sigma,
            },
            filename_prefix="gaussianblur",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}gaussianblur", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Line
class LF_Line:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor to draw a line upon."
                }),
                "start_x": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Horizontal position to begin the line drawing, expressed as a value between 0 and 1."
                }),
                "start_y": (Input.FLOAT, {
                    "default": 0,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Vertical position to begin the line drawing, expressed as a value between 0 and 1."
                }),
                "end_x": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Horizontal position to end the line drawing, expressed as a value between 0 and 1."
                }),
                "end_y": (Input.FLOAT, {
                    "default": 1,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Vertical position to end the line drawing, expressed as a value between 0 and 1."
                }),
                "size": (Input.INTEGER, {
                    "default": 10, 
                    "min": 1, 
                    "max": 500, 
                    "step": 1, 
                    "tooltip": "Diameter of the line in pixels."
                }),
                "color": (Input.STRING, {
                    "default": "FF0000", 
                    "tooltip": "Hex color of the line."
                }),
                "opacity": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01, 
                    "tooltip": "Opacity of the line."
                }),
                "smooth": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Draws a smooth line."
                }),
            },
            "optional": {
                "mid_x": (Input.FLOAT, {
                    "default": 0.25,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Horizontal midpoint of the line, expressed as a value between 0 and 1."
                }),
                "mid_y": (Input.FLOAT, {
                    "default": 0.25,
                    "min": 0,
                    "max": 1,
                    "tooltip": "Vertical midpoint of the line, expressed as a value between 0 and 1."
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        start_x: float = normalize_list_to_value(kwargs.get("start_x", 0))
        start_y: float = normalize_list_to_value(kwargs.get("start_y", 0))
        end_x: float = normalize_list_to_value(kwargs.get("end_x", 1))
        end_y: float = normalize_list_to_value(kwargs.get("end_y", 1))
        mid_x: float = normalize_list_to_value(kwargs.get("mid_x", (start_x + end_x) / 2))
        mid_y: float = normalize_list_to_value(kwargs.get("mid_y", (start_y + end_y) / 2))
        size: int = normalize_list_to_value(kwargs.get("size"))
        color: str = normalize_list_to_value(kwargs.get("color"))
        smooth: bool = normalize_list_to_value(kwargs.get("smooth"))
        opacity: float = normalize_list_to_value(kwargs.get("opacity"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        points: list[tuple] = [(start_x, start_y)]
        if smooth:
            points.append((mid_x, mid_y))
        points.append((end_x, end_y))

        processed_images = process_and_save_image(
            images=image,
            filter_function=line_effect,
            filter_args={
                'points': points,
                'size': size,
                'color': color,
                'opacity': opacity,
                "smooth": smooth
            },
            filename_prefix="line",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}line", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Saturation
class LF_Saturation:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 1.2, 
                    "min": 0.0, 
                    "max": 5.0, 
                    "step": 0.1, 
                    "tooltip": "1.0 = no change, <1 = desat, >1 = saturation boost."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs["intensity"])

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed = process_and_save_image(
            images=image,
            filter_function=saturation_effect,
            filter_args={
                "intensity": intensity
            },
            filename_prefix="saturation",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}saturation", {
            "node": kwargs.get("node_id"), 
            "dataset": dataset
        })

        return (batch_list[0], image_list)
# endregion    

# region LF_Sepia
class LF_Sepia:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the strength of the sepia effect."
                }),
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=sepia_effect,
            filter_args={
                'intensity': intensity,
            },
            filename_prefix="sepia",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}sepia", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Split tone
class LF_SplitTone:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Base image to colour-grade."
                }),
                "shadows_tint": (Input.STRING, {
                    "default": "0066FF",
                    "tooltip": "Hex colour applied to shadows (e.g. 0066FF)."
                }),
                "highlights_tint": (Input.STRING, {
                    "default": "FFAA55",
                    "tooltip": "Hex colour applied to highlights (e.g. FFAA55)."
                }),
                "balance": (Input.FLOAT, {
                    "default": 0.50, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Luminance pivot. 0 = lift even deep blacks; 1 = tint only the brightest pixels."
                    
                }),
                "softness": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": 0.01, 
                    "max": 0.5, 
                    "step": 0.01,
                    "tooltip": "Width of the transition band around the balance value."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.60, 
                    "min": 0.0, 
                    "max": 2.0, 
                    "step": 0.05,
                    "tooltip": "Strength of the tint applied."
                }),
            },
            "optional": {
                "ui_widget": ("LF_COMPARE", {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("image", "image_list")
    FUNCTION = FUNCTION
    CATEGORY = CATEGORY
    OUTPUT_IS_LIST = (False, True)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        shadows_tint: str = normalize_list_to_value(kwargs.get("shadows_tint", "0066FF"))
        highlights_tint: str = normalize_list_to_value(kwargs.get("highlights_tint", "FFAA55"))
        balance: float = normalize_list_to_value(kwargs.get("balance", 0.5))
        softness: float = normalize_list_to_value(kwargs.get("softness", 0.25))
        intensity: float = normalize_list_to_value(kwargs.get("intensity", 0.6))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=split_tone_effect,
            filter_args={
                'shadows_tint': shadows_tint,
                'highlights_tint': highlights_tint,
                'balance': balance,
                'softness': softness,
                'intensity': intensity
            },
            filename_prefix="splittone",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}splittone", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_TiltShift
class LF_TiltShift:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Image to miniature-ify."
                }),
                "focus_position": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Vertical centre of sharp band (0 = top, 1 = bottom)."
                }),
                "focus_size": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": 0.05, 
                    "max": 0.9, 
                    "step": 0.01,
                    "tooltip": "Height of sharp zone as fraction of image."
                }),
                "blur_radius": (Input.INTEGER, {
                    "default": 25, 
                    "min": 3, 
                    "max": 151, 
                    "step": 2,
                    "tooltip": "Gaussian radius for out-of-focus areas."
                }),
                "feather": (["linear", "smooth", "expo"], {
                    "default": "smooth",
                    "tooltip": "Fall-off curve of blur vs distance."
                }),
            },
            "optional": {
                "orientation": (["horizontal", "vertical", "circular"], {
                    "default": "horizontal",
                    "tooltip": "Direction of the focus band."
                }),
                "ui_widget": (Input.LF_COMPARE, {"default": {}})
            },
            "hidden": {"node_id": "UNIQUE_ID"}
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        focus_position: float = normalize_list_to_value(kwargs.get("focus_position"))
        focus_size: float = normalize_list_to_value(kwargs.get("focus_size"))
        blur_radius: int = normalize_list_to_value(kwargs.get("blur_radius"))
        feather: str = normalize_list_to_value(kwargs.get("feather", "smooth"))
        orientation: str = normalize_list_to_value(kwargs.get("orientation", "horizontal"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=tilt_shift_effect,
            filter_args={
                'focus_position': focus_position,
                'focus_size': focus_size,
                'blur_radius': blur_radius,
                'feather': feather,
                'orient': orientation
            },
            filename_prefix="tiltshift",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}tiltshift", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

# region LF_Vibrance
class LF_Vibrance:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE,  {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT,  {
                    "default": 0.6, 
                    "min": -1.0, 
                    "max": 2.0,
                    "step": 0.05,
                    "tooltip": "Negative = tame colours, positive = boost muted hues"
                }),
            },
            "optional": {
                "protect_skin": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Less push on hue-range 15-50° (common skin)"
                }),
                "clip_soft": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Roll saturation off near max to avoid clipping"
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": { "node_id": "UNIQUE_ID" }
        }
    
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        protect_skin: bool = normalize_list_to_value(kwargs.get("protect_skin", True))
        clip_soft: bool = normalize_list_to_value(kwargs.get("clip_soft", True))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=vibrance_effect,
            filter_args={
                'intensity': intensity,
                'protect_skin': protect_skin,
                'clip_soft': clip_soft
            },
            filename_prefix="vibrance",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}vibrance", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion
        
# region LF_Vignette
class LF_Vignette:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "intensity": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the darkness of the vignette effect. Higher values mean darker edges."
                }),
                "radius": (Input.FLOAT, {
                    "default": 0.75,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.05,
                    "tooltip": "Controls the size of the vignette effect. Lower values mean a smaller vignette."
                }),
                "shape": (["elliptical", "circular"], {
                    "default": "elliptical",
                    "tooltip": "Selects the shape of the vignette effect."
                }),
                "color": (Input.STRING, {
                    "default": "000000", 
                    "tooltip": "Color to use for padding if 'pad' mode is selected (hexadecimal)."
                })
            },
            "optional": {
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
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        intensity: float = normalize_list_to_value(kwargs.get("intensity"))
        radius: float = normalize_list_to_value(kwargs.get("radius"))
        shape: str = normalize_list_to_value(kwargs.get("shape", "elliptical"))
        color: str = normalize_list_to_value(kwargs.get("color", "000000"))

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        processed_images = process_and_save_image(
            images=image,
            filter_function=vignette_effect,
            filter_args={
                'intensity': intensity,
                'radius': radius,
                'shape': shape,
                'color': color,
            },
            filename_prefix="vignette",
            nodes=nodes,
        )

        batch_list, image_list = normalize_output_image(processed_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}vignette", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (batch_list[0], image_list)
# endregion

NODE_CLASS_MAPPINGS = {
    "LF_Blend": LF_Blend,
    "LF_Bloom": LF_Bloom,
    "LF_Brightness": LF_Brightness,
    "LF_Clarity": LF_Clarity,
    "LF_Contrast": LF_Contrast,
    "LF_Desaturation": LF_Desaturation,
    "LF_FilmGrain": LF_FilmGrain,
    "LF_GaussianBlur": LF_GaussianBlur,
    "LF_Line": LF_Line,
    "LF_Saturation": LF_Saturation,
    "LF_Sepia": LF_Sepia,
    "LF_SplitTone": LF_SplitTone,
    "LF_TiltShift": LF_TiltShift,
    "LF_Vibrance": LF_Vibrance,
    "LF_Vignette": LF_Vignette
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Blend": "Blend",
    "LF_Bloom": "Bloom",
    "LF_Brightness": "Brightness",
    "LF_Clarity": "Clarity",
    "LF_Contrast": "Contrast",
    "LF_Desaturation": "Desaturation",
    "LF_FilmGrain": "Film grain",
    "LF_GaussianBlur": "Gaussian Blur",
    "LF_Line": "Line",
    "LF_Saturation": "Saturation",
    "LF_Sepia": "Sepia",
    "LF_SplitTone": "Split Tone",
    "LF_TiltShift": "Tilt Shift",
    "LF_Vibrance": "Vibrance",
    "LF_Vignette": "Vignette"
}