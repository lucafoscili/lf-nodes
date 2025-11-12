import torch

from typing import Any, List, Optional

from ..conversion.tensor_to_base64 import tensor_to_base64

# region build_openai_multimodal_content
def build_openai_multimodal_content(
    image: Optional[torch.Tensor | List[torch.Tensor]],
    text: str,
    base64_prefix: str = "data:image/png;charset=utf-8;base64,"
) -> List[dict[str, Any]]:
    """
    Build multimodal content array for OpenAI-style APIs.

    Args:
        image: Optional image tensor or list of tensors to include (uses first if list)
        text: Text prompt to include
        base64_prefix: Prefix for base64 encoded images (default PNG)

    Returns:
        List of content items for the message
    """
    content = []

    if image is not None and (not isinstance(image, list) or len(image) > 0):
        # Handle both single tensor and list of tensors
        if isinstance(image, list) and len(image) > 0:
            image_tensor = image[0]
        else:
            image_tensor = image

        base64_data = tensor_to_base64(image_tensor)
        if isinstance(base64_data, list):
            base64_data = base64_data[0]

        image_url = f"{base64_prefix}{base64_data}"
        content.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    if text:
        content.append({
            "type": "text",
            "text": text
        })

    return content
# endregion