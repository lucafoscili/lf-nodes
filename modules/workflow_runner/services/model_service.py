import logging
import aiohttp
from typing import List, Dict, Any
import folder_paths

from ..config import get_settings
from .proxy_service import _read_secret

LOG = logging.getLogger(__name__)

async def get_gemini_models() -> List[str]:
    """
    Retrieve available Gemini models from the Google Generative AI API.

    Returns:
        List of model names.
    """
    api_key = _read_secret("GEMINI_API_KEY", "GEMINI_API_KEY_FILE")
    if not api_key:
        LOG.warning("GEMINI_API_KEY not set, cannot retrieve Gemini models")
        return []

    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {"x-goog-api-key": api_key}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    # Extract model names, e.g., "models/gemini-2.0-flash-exp" -> "gemini-2.0-flash-exp"
                    model_names = [model["name"].split("/")[-1] for model in models if "name" in model]
                    # Filter to only include models that start with "gemini-"
                    gemini_models = [name for name in model_names if name.startswith("gemini-")]
                    return gemini_models
                else:
                    LOG.error(f"Failed to retrieve Gemini models: {response.status} {await response.text()}")
                    return []
    except Exception as exc:
        LOG.exception("Error retrieving Gemini models")
        return []

def get_comfy_models() -> List[str]:
    """
    Retrieve available ComfyUI models from checkpoints and diffusion_models folders.

    Returns:
        List of model filenames.
    """
    try:
        checkpoints = folder_paths.get_filename_list("checkpoints")
        diffusion_models = folder_paths.get_filename_list("diffusion_models")
        # Merge and remove duplicates
        all_models = list(set(checkpoints + diffusion_models))
        return all_models
    except Exception as exc:
        LOG.exception("Error retrieving Comfy models")
        return []

async def get_all_models() -> Dict[str, Any]:
    """
    Retrieve all available models from all engines.

    Returns:
        Dict with "engines" key containing list of engine dicts.
    """
    gemini_models = await get_gemini_models()
    comfy_models = get_comfy_models()

    engines = [
        {
            "name": "Gemini (Google)",
            "models": gemini_models
        },
        {
            "name": "Diffusion (Comfy)",
            "models": comfy_models
        }
    ]

    return {"engines": engines}