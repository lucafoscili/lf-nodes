import torch

from ....utils.helpers.conversion.base64_to_tensor import base64_to_tensor

# region parse_gemini_image
def parse_gemini_image(response_data: dict) -> torch.Tensor | None:
    """
    Extracts image data from Gemini API response.
    
    Args:
        response_data: The JSON response from Gemini API
        
    Returns:
        torch.Tensor or None: The decoded image tensor if found
    """
    if not isinstance(response_data, dict):
        return None
    
    candidates = response_data.get("candidates", [])
    if not candidates or not isinstance(candidates, list):
        return None
    
    first_candidate = candidates[0]
    if not isinstance(first_candidate, dict):
        return None
    
    content = first_candidate.get("content")
    if not content or not isinstance(content, dict):
        return None
    
    parts = content.get("parts", [])
    if not isinstance(parts, list):
        return None
    
    for part in parts:
        if isinstance(part, dict) and "inline_data" in part:
            inline_data = part["inline_data"]
            if isinstance(inline_data, dict) and "data" in inline_data:
                base64_data = inline_data["data"]
                try:
                    return base64_to_tensor(base64_data)
                except Exception:
                    pass
    
    return None
# endregion