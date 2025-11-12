import aiohttp
import os
import torch

from typing import Any

from server import PromptServer

from . import CATEGORY
from ...utils.constants import API_ROUTE_PREFIX, FUNCTION, Input
from ...utils.helpers.api import create_ui_logger, read_secret
from ...utils.helpers.conversion.base64_to_tensor import base64_to_tensor

# region LF_StabilityAPI
class LF_StabilityAPI:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "prompt": (Input.STRING, {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Text prompt to generate image from."
                }),
            },
            "optional": {
                "model": (Input.STRING, {
                    "default": "stable-diffusion-xl-1024-v1-0",
                    "tooltip": "Stability AI model to use for generation."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Negative prompt to avoid in generation."
                }),
                "width": (Input.INTEGER, {
                    "default": 512,
                    "min": 64,
                    "max": 2048,
                    "step": 64,
                    "tooltip": "Width of generated image."
                }),
                "height": (Input.INTEGER, {
                    "default": 512,
                    "min": 64,
                    "max": 2048,
                    "step": 64,
                    "tooltip": "Height of generated image."
                }),
                "steps": (Input.INTEGER, {
                    "default": 20,
                    "min": 10,
                    "max": 150,
                    "step": 1,
                    "tooltip": "Number of diffusion steps."
                }),
                "cfg_scale": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 35.0,
                    "step": 0.1,
                    "tooltip": "Classifier-free guidance scale."
                }),
                "samples": (Input.INTEGER, {
                    "default": 1,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "Number of images to generate."
                }),
                "style_preset": (["", "enhance", "anime", "photographic", "digital-art", "comic-book", "fantasy-art", "line-art", "analog-film", "neon-punk", "isometric", "low-poly", "origami", "modeling-compound", "cinematic", "3d-model", "pixel-art", "tile-texture"], {
                    "tooltip": "Style preset to use for generation."
                }),
                "timeout": (Input.INTEGER, {
                    "default": 120,
                    "tooltip": "Request timeout in seconds."
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Generated images from Stability AI.",
    )
    RETURN_NAMES = ("images",)
    RETURN_TYPES = (Input.IMAGE,)

    async def on_exec(self, **kwargs: dict) -> tuple:
        prompt: str = kwargs.get("prompt", "")
        model: str = kwargs.get("model") or "stable-diffusion-v1-6"
        negative_prompt: str = kwargs.get("negative_prompt", "")
        width: int = int(kwargs.get("width", 512))
        height: int = int(kwargs.get("height", 512))
        steps: int = int(kwargs.get("steps", 20))
        cfg_scale: float = float(kwargs.get("cfg_scale", 7.0))
        samples: int = int(kwargs.get("samples", 1))
        style_preset: str = kwargs.get("style_preset", "")
        logger = create_ui_logger("stabilityapi", kwargs.get("node_id"))

        logger.log("Sending generation request...")

        proxy_url = os.environ.get("STABILITY_PROXY_URL")
        if not proxy_url:
            try:
                ps_inst = getattr(PromptServer, 'instance', None)
                host = getattr(ps_inst, 'address', None)
                port = getattr(ps_inst, 'port', None)
                if host and port:
                    if host in ("0.0.0.0", "::"):
                        host = "localhost"
                    proxy_url = f"http://{host}:{port}{API_ROUTE_PREFIX}/proxy/stability"
                elif os.environ.get("DEV_ENV") == "1":
                    proxy_url = f"http://localhost:8080{API_ROUTE_PREFIX}/proxy/stability"
            except Exception:
                if os.environ.get("DEV_ENV") == "1":
                    proxy_url = f"http://localhost:8080{API_ROUTE_PREFIX}/proxy/stability"

        if not proxy_url:
            logger.log("No proxy URL configured. Set STABILITY_PROXY_URL environment variable or ensure PromptServer is running.")
            raise ValueError("No proxy URL configured. Set STABILITY_PROXY_URL environment variable or ensure PromptServer is running.")

        timeout_sec: int = int(kwargs.get("timeout", 120) or 120)

        if not prompt:
            logger.log("Prompt must not be empty.")
            raise ValueError("Prompt must not be empty.")

        text_prompts = [{"text": prompt, "weight": 1}]
        if negative_prompt:
            text_prompts.append({"text": negative_prompt, "weight": -1})

        payload: dict[str, Any] = {
            "model": model,
            "text_prompts": text_prompts,
            "cfg_scale": cfg_scale,
            "height": height,
            "width": width,
            "samples": samples,
            "steps": steps
        }

        if style_preset:
            payload["style_preset"] = style_preset

        headers = {"Content-Type": "application/json"}
        proxy_secret = read_secret("LF_PROXY_SECRET") or read_secret("STABILITY_PROXY_SECRET")
        if proxy_secret:
            headers["X-LF-Proxy-Secret"] = proxy_secret

        injected_session = kwargs.get("_test_session")
        session_cm = injected_session if injected_session is not None else aiohttp.ClientSession()
        async with session_cm as session:
            async with session.post(proxy_url, headers=headers, json=payload, timeout=timeout_sec) as resp:
                text_status = await resp.text()
                try:
                    data = await resp.json()
                except Exception:
                    logger.log("Failed to parse JSON response.")
                    raise ValueError(f"Failed to parse response: {text_status}")

        if resp.status != 200:
            logger.log(f"Error from Stability API: {resp.status} {text_status}")
            raise ValueError(f"Stability API error: {resp.status} - {text_status}")

        if isinstance(data, dict):
            data.setdefault("lf_http_status", resp.status)
        else:
            data = {"response": data, "lf_http_status": resp.status}

        # Parse generated images from response
        generated_images = []
        if "artifacts" in data:
            for artifact in data["artifacts"]:
                if "base64" in artifact:
                    try:
                        # Convert base64 to tensor
                        image_tensor = base64_to_tensor(artifact["base64"])
                        generated_images.append(image_tensor)
                    except Exception as e:
                        logger.log(f"Failed to decode image: {e}")
                        continue

        if not generated_images:
            logger.log("No images were generated.")
            raise ValueError("No images were generated from Stability AI.")

        # Stack images into a batch
        if len(generated_images) == 1:
            result_images = generated_images[0]
        else:
            result_images = torch.cat(generated_images, dim=0)

        logger.log(f"Successfully generated {len(generated_images)} image(s).")

        return (result_images,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_StabilityAPI": LF_StabilityAPI,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_StabilityAPI": "Stability AI (Image Gen)",
}
# endregion