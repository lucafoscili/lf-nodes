import os
import json
import os
import torch

from aiohttp import web
from PIL import Image

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX
from ..utils.filters import blend_effect, bloom_effect, brightness_effect, clarity_effect, contrast_effect, desaturate_effect, film_grain_effect, gaussian_blur_effect, line_effect, saturation_effect, sepia_effect, split_tone_effect, tilt_shift_effect, vibrance_effect, vignette_effect
from ..utils.helpers import base64_to_tensor, convert_to_boolean, convert_to_float, convert_to_int, create_colored_tensor, create_masonry_node, get_comfy_dir, get_resource_url, pil_to_tensor, resolve_filepath, resolve_url, tensor_to_pil

# region get-image
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-image")
async def get_images_in_directory(request):
    try:
        r: dict = await request.post()
        
        directory: str = r.get("directory")

        if (directory):
            images_dir = os.path.join(get_comfy_dir("input"), directory)
        else:
            images_dir = get_comfy_dir("input")
        if not os.path.exists(images_dir):
            return web.Response(status=404, text="Directory not found.")

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        for index, filename in enumerate(os.listdir(images_dir)):
            file_path = os.path.join(images_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                url = get_resource_url(directory, filename, "input")
                nodes.append(create_masonry_node(filename, url, index))

        return web.json_response({
            "status": "success",
            "data": dataset
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region process-image
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/process-image")
async def process_image(request):
    try:
        r: dict = await request.post()

        api_url: str = r.get("url")
        filter_type: str = r.get("type")
        settings: dict = json.loads(r.get("settings"))

        filename, file_type, subfolder = resolve_url(api_url)

        if not filename or not file_type:
            return web.Response(status=400, text="Missing required URL parameters.")

        images_dir = os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

        if not os.path.exists(images_dir):
            return web.Response(status=404, text="Image not found.")
        
        img_tensor = load_image_tensor(images_dir)

        if filter_type == "blend":
            processed_tensor = apply_blend_effect(img_tensor, settings)
        elif filter_type == "bloom":
            processed_tensor = apply_bloom_effect(img_tensor, settings)           
        elif filter_type == "brightness":
            processed_tensor = apply_brightness_effect(img_tensor, settings)
        elif filter_type == "brush":
            processed_tensor = apply_brush_effect(img_tensor, settings)
        elif filter_type == "clarity":
            processed_tensor = apply_clarity_effect(img_tensor, settings)
        elif filter_type == "contrast":
            processed_tensor = apply_contrast_effect(img_tensor, settings)
        elif filter_type == "desaturate":
            processed_tensor = apply_desaturate_effect(img_tensor, settings)
        elif filter_type == "film_grain":
            processed_tensor = apply_film_grain_effect(img_tensor, settings)
        elif filter_type == "gaussian_blur":
            processed_tensor = apply_gaussian_blur_effect(img_tensor, settings)
        elif filter_type == "line":
            processed_tensor = apply_line_effect(img_tensor, settings)
        elif filter_type == "saturation":
            processed_tensor = apply_saturation_effect(img_tensor, settings)
        elif filter_type == "sepia":
            processed_tensor = apply_sepia_effect(img_tensor, settings)
        elif filter_type == "split_tone":
            processed_tensor = apply_split_tone_effect(img_tensor, settings)
        elif filter_type == "tilt_shift":
            processed_tensor = apply_tilt_shift_effect(img_tensor, settings)
        elif filter_type == "vibrance":
            processed_tensor = apply_vibrance_effect(img_tensor, settings)
        elif filter_type == "vignette":
            processed_tensor = apply_vignette_effect(img_tensor, settings)
        else:
            return web.Response(status=400, text=f"Unsupported filter type: {filter_type}")

        pil_image = tensor_to_pil(processed_tensor)
        output_file, subfolder, filename = resolve_filepath(filename_prefix=filter_type, image=img_tensor)
        pil_image.save(output_file, format="PNG")

        return web.json_response({
            "status": "success",
            "data": get_resource_url(subfolder, filename, "temp")
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region helpers
def apply_blend_effect(img_tensor: torch.Tensor, settings: dict):
    opacity = convert_to_float(settings.get("opacity", 1.0))
    color: str = settings.get("color", "FF0000")

    overlay_image = create_colored_tensor(img_tensor, color)

    return blend_effect(img_tensor, overlay_image, opacity)

def apply_bloom_effect(img_tensor: torch.Tensor, settings: dict):
    intensity = convert_to_float(settings.get("intensity", 0))
    radius = convert_to_int(settings.get("radius", 0))
    threshold = convert_to_float(settings.get("threshold", 0))
    tint = settings.get("tint", "FFFFFF")

    return bloom_effect(img_tensor, threshold, radius, intensity, tint)

def apply_brightness_effect(img_tensor: torch.Tensor, settings: dict):
    brightness_strength = convert_to_float(settings.get("strength", 0))
    gamma = convert_to_float(settings.get("gamma", 0))
    midpoint = convert_to_float(settings.get("midpoint", 0))
    localized_brightness = convert_to_boolean(settings.get("localized", False))

    return brightness_effect(img_tensor, brightness_strength, gamma, midpoint, localized_brightness)

def apply_brush_effect(img_tensor: torch.Tensor, settings: dict):
    b64_canvas: str = settings.get("b64_canvas", "")
    canvas = base64_to_tensor(b64_canvas, True)

    return blend_effect(img_tensor, canvas, 1.0)

def apply_clarity_effect(img_tensor: torch.Tensor, settings: dict):
    clarity_strength = convert_to_float(settings.get("clarity_strength", 0))
    sharpen_amount = convert_to_float(settings.get("sharpen_amount", 0))
    blur_kernel_size = convert_to_int(settings.get("blur_kernel_size", 1))

    return clarity_effect(img_tensor, clarity_strength, sharpen_amount, blur_kernel_size)

def apply_contrast_effect(img_tensor: torch.Tensor, settings: dict):
    contrast_strength = convert_to_float(settings.get("strength", 0))
    midpoint = convert_to_float(settings.get("midpoint", 0))
    localized_contrast = convert_to_boolean(settings.get("localized", False))

    return contrast_effect(img_tensor, contrast_strength, midpoint, localized_contrast)

def apply_desaturate_effect(img_tensor: torch.Tensor, settings: dict):
    desaturation_strength = convert_to_float(settings.get("strength", 0))
    r = convert_to_float(settings.get("r_channel", 1))
    g = convert_to_float(settings.get("g_channel", 1))
    b = convert_to_float(settings.get("b_channel", 1))

    return desaturate_effect(img_tensor, desaturation_strength, [r, g, b])

def apply_film_grain_effect(img_tensor: torch.Tensor, settings: dict):
    intensity: float = convert_to_float(settings.get("intensity", 0))
    size: float = convert_to_float(settings.get("size", 1))
    tint: str = settings.get("tint", "FFFFFF")
    soft_blend: bool = convert_to_boolean(settings.get("soft_blend", False))

    return film_grain_effect(img_tensor, intensity, size, tint, soft_blend)

def apply_gaussian_blur_effect(img_tensor: torch.Tensor, settings: dict):
    blur_sigma = convert_to_float(settings.get("blur_sigma", 0))
    blur_kernel_size = convert_to_int(settings.get("blur_kernel_size", 1))

    return gaussian_blur_effect(img_tensor, blur_kernel_size, blur_sigma)

def apply_line_effect(img_tensor: torch.Tensor, settings: dict):
    points: list = settings.get("points", [])
    points: list[tuple] = [(point["x"], point["y"]) for point in points]
    
    size = convert_to_int(settings.get("size", 0))
    color: str = settings.get("color", "FF0000")
    opacity = convert_to_float(settings.get("opacity", 1))
    smooth = convert_to_boolean(settings.get("smoooth", False))

    return line_effect(img_tensor, points, size, color, opacity, smooth)

def apply_saturation_effect(img_tensor: torch.Tensor, settings: dict):
    intensity = convert_to_float(settings.get("intensity", 1))

    return saturation_effect(img_tensor, intensity)

def apply_sepia_effect(img_tensor: torch.Tensor, settings: dict):
    intensity = convert_to_float(settings.get("intensity", 0))

    return sepia_effect(img_tensor, intensity)

def apply_split_tone_effect(img_tensor: torch.Tensor, settings: dict):
    highlights: str = settings.get("highlights", "FFAA55")
    shadows: str = settings.get("shadows", "0066FF")
    balance = convert_to_float(settings.get("balance", 0))
    softness = convert_to_float(settings.get("softness", 0))
    intensity = convert_to_float(settings.get("intensity", 0))

    return split_tone_effect(img_tensor, shadows, highlights, balance, softness, intensity)

def apply_tilt_shift_effect(img_tensor: torch.Tensor, settings: dict):
    focus_position = convert_to_float(settings.get("focus_position", 0.5))
    focus_size = convert_to_float(settings.get("focus_size", 0.25))
    blur_radius = convert_to_int(settings.get("radius", 25))
    feather: str = settings.get("feather", "smooth")
    orientation: str = settings.get("orientation", "horizontal")

    return tilt_shift_effect(img_tensor, focus_position, focus_size, blur_radius, feather, orientation)

def apply_vibrance_effect(img_tensor: torch.Tensor, settings: dict):
    intensity: float= convert_to_float(settings.get("intensity", 0))
    protect_skin: bool = convert_to_boolean(settings.get("protect_skin", False))
    clip_soft: bool = convert_to_boolean(settings.get("clip_soft", False))

    return vibrance_effect(img_tensor, intensity, protect_skin, clip_soft)

def apply_vignette_effect(img_tensor: torch.Tensor, settings: dict):
    intensity = convert_to_float(settings.get("intensity", 0))
    radius = convert_to_float(settings.get("radius", 0))
    shape: str = settings.get("shape", "elliptical")
    color: str = settings.get("color", "000000")

    return vignette_effect(img_tensor, intensity, radius, shape, color)

def load_image_tensor(image_path: str) -> torch.Tensor:
    try:
        pil_image = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    img_tensor = pil_to_tensor(pil_image)

    return img_tensor
# endregion