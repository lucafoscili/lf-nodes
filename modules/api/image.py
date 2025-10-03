import json
import os
import torch

from aiohttp import web
from PIL import Image

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX, IMAGE_FILE_EXTENSIONS
from ..utils.filters.processors import UnknownFilterError, process_filter
from ..utils.helpers.api import get_resource_url, resolve_url
from ..utils.helpers.comfy import (
    ensure_external_preview,
    get_comfy_dir,
    resolve_filepath,
    resolve_input_directory_path,
)
from ..utils.helpers.conversion import pil_to_tensor, tensor_to_pil
from ..utils.helpers.logic import sanitize_filename
from ..utils.helpers.ui import create_masonry_node

# region get-image
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-image")
async def get_images_in_directory(request):
    try:
        r: dict = await request.post()

        raw_directory: str = r.get("directory")
        images_dir, resolved_directory, is_external = resolve_input_directory_path(raw_directory)
        if images_dir is None or not os.path.exists(images_dir):
            return web.Response(status=404, text="Directory not found.")

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        navigation_directory: dict[str, object] = {}
        if isinstance(raw_directory, str):
            navigation_directory["raw"] = raw_directory
        if images_dir:
            navigation_directory["resolved"] = images_dir
        if resolved_directory is not None:
            navigation_directory["relative"] = resolved_directory
        navigation_directory["is_external"] = is_external

        dataset["navigation"] = {"directory": navigation_directory}

        for index, filename in enumerate(os.listdir(images_dir)):
            file_path = os.path.join(images_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith(IMAGE_FILE_EXTENSIONS):
                if is_external:
                    try:
                        preview_subfolder, preview_name = ensure_external_preview(images_dir, filename)
                    except FileNotFoundError:
                        continue
                    url = get_resource_url(preview_subfolder, preview_name, "input")
                else:
                    url = get_resource_url(resolved_directory or "", filename, "input")
                nodes.append(create_masonry_node(filename, url, index))

        return web.json_response(
            {
                "status": "success",
                "data": dataset,
            },
            status=200,
        )

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
        settings_raw = r.get("settings") or "{}"
        settings: dict = json.loads(settings_raw)

        filename, file_type, subfolder = resolve_url(api_url)

        if not filename or not file_type:
            return web.Response(status=400, text="Missing required URL parameters.")

        images_dir = os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

        if not os.path.exists(images_dir):
            return web.Response(status=404, text="Image not found.")

        img_tensor = load_image_tensor(images_dir)

        try:
            processed_tensor, extra_payload = process_filter(filter_type, img_tensor, settings)
        except UnknownFilterError as exc:
            return web.Response(status=400, text=str(exc))

        save_type: str = str(settings.get("resource_type") or settings.get("output_type") or "temp")
        base_output_path = get_comfy_dir(save_type)

        custom_subfolder_raw = settings.get("subfolder")
        if isinstance(custom_subfolder_raw, str) and custom_subfolder_raw.strip():
            normalized_subfolder = os.path.normpath(custom_subfolder_raw.strip()).strip("\\/")
            if normalized_subfolder.startswith(".."):
                return web.Response(status=400, text="Invalid subfolder path.")
        else:
            normalized_subfolder = ""

        filename_prefix_override = settings.get("filename_prefix")
        if isinstance(filename_prefix_override, str) and filename_prefix_override.strip():
            filename_prefix_value = filename_prefix_override.strip()
        else:
            filename_prefix_value = filter_type

        custom_filename_raw = settings.get("filename")
        if isinstance(custom_filename_raw, str) and custom_filename_raw.strip():
            sanitized_name = sanitize_filename(custom_filename_raw)
            if sanitized_name is None:
                return web.Response(status=400, text="Invalid filename provided.")

            filename_value = sanitized_name
            _, ext = os.path.splitext(filename_value)

            output_folder = os.path.join(base_output_path, normalized_subfolder) if normalized_subfolder else base_output_path
            os.makedirs(output_folder, exist_ok=True)

            output_file = os.path.join(output_folder, filename_value)
            output_folder_abs = os.path.abspath(output_folder)
            output_file_abs = os.path.abspath(output_file)
            if os.path.commonpath([output_folder_abs, output_file_abs]) != output_folder_abs:
                return web.Response(status=400, text="Filename resolves outside of the target directory.")

            final_subfolder = normalized_subfolder.replace("\\", "/") if normalized_subfolder else ""
        else:
            prefixed_name = os.path.join(normalized_subfolder, filename_prefix_value) if normalized_subfolder else filename_prefix_value
            output_file, final_subfolder_raw, filename_value = resolve_filepath(
                filename_prefix=prefixed_name,
                base_output_path=base_output_path,
                image=img_tensor,
            )
            final_subfolder = (final_subfolder_raw or "").replace("\\", "/")
            _, ext = os.path.splitext(filename_value)

        pil_image = tensor_to_pil(processed_tensor)

        ext_lower = ext.lower()
        format_map = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".webp": "WEBP",
            ".bmp": "BMP",
            ".gif": "GIF",
        }
        save_format = format_map.get(ext_lower, "PNG")
        pil_image.save(output_file, format=save_format)

        payload = {
            "status": "success",
            "data": get_resource_url(final_subfolder, filename_value, save_type),
            "type": save_type,
            "subfolder": final_subfolder,
            "filename": filename_value,
        }
        if extra_payload:
            payload.update(extra_payload)

        return web.json_response(payload, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region helpers
def load_image_tensor(image_path: str) -> torch.Tensor:
    try:
        pil_image = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise ValueError(f"Error opening image: {e}")

    img_tensor = pil_to_tensor(pil_image)

    return img_tensor
# endregion
