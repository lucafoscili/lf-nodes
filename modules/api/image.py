import json
import os
import torch

from aiohttp import web
from PIL import Image

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX
from ..utils.filters.processors import UnknownFilterError, process_filter
from ..utils.helpers.api import get_resource_url, resolve_url
from ..utils.helpers.comfy import get_comfy_dir, resolve_filepath
from ..utils.helpers.conversion import pil_to_tensor, tensor_to_pil
from ..utils.helpers.ui import create_masonry_node

# region get-image
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/get-image")
async def get_images_in_directory(request):
    try:
        r: dict = await request.post()

        directory: str = r.get("directory")

        if directory:
            images_dir = os.path.join(get_comfy_dir("input"), directory)
        else:
            images_dir = get_comfy_dir("input")
        if not os.path.exists(images_dir):
            return web.Response(status=404, text="Directory not found.")

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        for index, filename in enumerate(os.listdir(images_dir)):
            file_path = os.path.join(images_dir, filename)
            if os.path.isfile(file_path) and filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                url = get_resource_url(directory, filename, "input")
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

        pil_image = tensor_to_pil(processed_tensor)
        output_file, subfolder, filename = resolve_filepath(
            filename_prefix=filter_type,
            image=img_tensor,
        )
        pil_image.save(output_file, format="PNG")

        payload = {
            "status": "success",
            "data": get_resource_url(subfolder, filename, "temp"),
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
