import base64
import json
import os
import asyncio
import aiohttp
from aiohttp import web, ClientError
from folder_paths import get_full_path
from PIL import Image, UnidentifiedImageError
from io import BytesIO

from ..utils.constants import API_ROUTE_PREFIX, BASE64_PNG_PREFIX
from ..utils.helpers.comfy import get_comfy_list

from server import PromptServer

# region clear-metadata
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/clear-metadata")
async def clear_model_info(_):
    try:
        directories = [
            ("checkpoints", get_comfy_list("checkpoints")),
            ("embeddings", get_comfy_list("embeddings")),
            ("loras", get_comfy_list("loras"))
        ]

        deleted_files: list = []

        for folder_name, directory in directories:
            for model_file in directory:
                model_full_path = get_full_path(folder_name, model_file)

                if model_full_path is None:
                    continue

                file_no_ext = os.path.splitext(model_full_path)[0]
                info_file_path = file_no_ext + ".info"

                if os.path.exists(info_file_path):
                    try:
                        os.remove(info_file_path)
                        deleted_files.append(info_file_path)
                    except Exception as e:
                        return web.Response(status=500, text=f"Failed to delete {info_file_path}: {str(e)}")

        return web.json_response({
            "status": "success",
            "message": f"Deleted {len(deleted_files)} .info files.",
            "deleted_files": deleted_files
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region save-metadata
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/save-metadata")
async def save_model_info(request):
    try:
        r: dict = await request.post()

        metadata = r.get("metadata")
        model_path = r.get("model_path")
        forced_save = r.get("forced_save")

        if not model_path or not metadata:
            return web.Response(status=400, text="Missing 'model_path' or 'metadata'.")

        metadata_json = json.loads(metadata)
        image_url = metadata_json.get("nodes", [])[0].get("cells", {}).get("lfImage", {}).get("value")

        file_no_ext = os.path.splitext(model_path)[0]
        info_file_path = file_no_ext + ".info"

        if os.path.exists(info_file_path):
            if bool(forced_save):
                os.remove(info_file_path)
            else:
                return web.json_response({"status": "warning", "message": f"Metadata already saved at {info_file_path}."}, status=200)

        if image_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(image_url, timeout=5) as head:
                        ctype = head.headers.get("Content-Type", "").lower()

                if not ctype.startswith("image/"):
                    metadata_json["nodes"][0]["cells"]["lfImage"]["value"] = None
                else:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url, timeout=10) as resp:
                            resp.raise_for_status()
                            data = await resp.read()

                    try:
                        with Image.open(BytesIO(data)) as probe:
                            probe.verify()
                    except (UnidentifiedImageError, OSError):
                        metadata_json["nodes"][0]["cells"]["lfImage"]["value"] = None
                    else:
                        try:
                            img = Image.open(BytesIO(data)).convert("RGB")
                            img.thumbnail((1024, 1024), Image.LANCZOS)

                            buf = BytesIO()
                            img.save(buf, format="JPEG", quality=85)
                            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                            metadata_json["nodes"][0]["cells"]["lfImage"]["value"] = f"{BASE64_PNG_PREFIX}{b64}"
                        except (UnidentifiedImageError, OSError) as processing_error:
                            metadata_json["nodes"][0]["cells"]["lfImage"]["value"] = None
                        except Exception as processing_error:
                            return web.Response(status=500, text=f"Error processing media: {processing_error}")
            except (ClientError, asyncio.TimeoutError) as network_error:
                metadata_json["nodes"][0]["cells"]["lfImage"]["value"] = None
            except Exception as e:
                return web.Response(status=500, text=f"Unexpected error while fetching media: {e}")

        with open(info_file_path, "w") as info_file:
            json.dump(metadata_json, info_file, indent=4)

        return web.json_response({"status": "success", "message": f"Metadata saved at {info_file_path}."}, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region update-metadata-cover
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/update-metadata-cover")
async def update_metadata_cover(request):
    try:
        r: dict = await request.post()

        model_path = r.get("model_path")
        base64_image = r.get("base64_image")

        if not model_path or not base64_image:
            return web.Response(status=400, text="Missing 'model_path' or 'base64_image'.")

        file_no_ext = os.path.splitext(model_path)[0]
        info_file_path = file_no_ext + ".info"

        if not os.path.exists(info_file_path):
            sha_file_path = file_no_ext + ".sha256"
            if os.path.exists(sha_file_path):
                with open(sha_file_path, "r") as sha_file:
                    model_hash = sha_file.read().strip()
            else:
                model_hash = "unknown"

            metadata_json = {
                "nodes": [
                    {
                        "cells": {
                            "lfCode": {
                                "shape": "code",
                                "value": {
                                    'hash': f'{model_hash}',
                                    'path': f'{model_path}'
                                },
                            },
                            "lfImage": {
                                "shape": "image",
                                "value": ""
                            },
                            "text1": {
                                "value": os.path.basename(model_path).rsplit('.', 1)[0]
                            },
                            "text2": {
                                "value": "Version unknown"
                            },
                            "text3": {
                                "value": "No info available"
                            }
                        },
                        "id": "node_1",
                        "value": ""
                    }
                ]
            }
            with open(info_file_path, "w") as info_file:
                json.dump(metadata_json, info_file, indent=4)

        with open(info_file_path, "r") as info_file:
            metadata_json = json.load(info_file)

        if "nodes" not in metadata_json or not metadata_json["nodes"]:
            metadata_json["nodes"] = [{}]

        if "cells" not in metadata_json["nodes"][0]:
            metadata_json["nodes"][0]["cells"] = {}

        try:
            img_data = base64.b64decode(base64_image.split(",")[-1])
            with Image.open(BytesIO(img_data)) as img:
                img = img.convert("RGB")
                img.thumbnail((1024, 1024), Image.LANCZOS)

                buf = BytesIO()
                img.save(buf, format="JPEG", quality=85)
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                base64_image = f"{BASE64_PNG_PREFIX}{b64}"
        except (UnidentifiedImageError, OSError) as processing_error:
            return web.Response(status=400, text=f"Invalid image data: {processing_error}")

        lf_image_cell = metadata_json["nodes"][0]["cells"].get("lfImage", {})
        lf_image_cell["value"] = f"{base64_image}"
        metadata_json["nodes"][0]["cells"]["lfImage"] = lf_image_cell

        with open(info_file_path, "w") as info_file:
            json.dump(metadata_json, info_file, indent=4)

        return web.json_response({"status": "success", "message": f"Cover updated in {info_file_path}."}, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion
