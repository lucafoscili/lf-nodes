import aiohttp
import folder_paths
import logging

from typing import List, Dict, Any

from .proxy_service import _read_secret

LOG = logging.getLogger(__name__)

#region Gemini models
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

    url = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=1000"
    headers = {"x-goog-api-key": api_key}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    model_names = [model["name"].split("/")[-1] for model in models if "name" in model]
                    return model_names
                else:
                    LOG.error(f"Failed to retrieve Gemini models: {response.status} {await response.text()}")
                    return []
    except Exception as exc:
        LOG.exception("Error retrieving Gemini models")
        return []
#endregion

#region Comfy models
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
#endregion

#region All models
async def get_all_models(is_image_models: bool = False) -> Dict[str, Any]:
    """
    Retrieve all available models from all engines.

    Args:
        is_image_models (bool): Flag indicating whether to retrieve image models.

    Returns:
        Dict with "engines" key containing list of engine dicts.
    """
    gemini_models = await get_gemini_models()
    comfy_models = get_comfy_models() 

    if is_image_models:
        engines = [
            {
                "name": "Diffusion (Comfy)",
                "models": comfy_models
            }
        ]
    else:
        engines = [
            {
                "name": "Gemini (Google)",
                "models": gemini_models
            },
        ]
    
    return {"engines": engines}
#endregion