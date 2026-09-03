import torch

from typing import Any, List, Optional

from ...constants import PNG_DATA_URL_PREFIX
from ..conversion.tensor_to_base64 import tensor_to_base64

# region build_openai_multimodal_content
def build_openai_multimodal_content(
    image: Optional[torch.Tensor | List[torch.Tensor]],
    text: str,
    base64_prefix: str = PNG_DATA_URL_PREFIX,
    *,
    include_all_images: bool = False,
) -> List[dict[str, Any]]:
    """
    Build multimodal content array for OpenAI-style APIs.

    Args:
        image: Optional image tensor or list of tensors to include
        text: Text prompt to include
        base64_prefix: Prefix for base64 encoded images (default PNG)
        include_all_images: Include every list item instead of only the first

    Returns:
        List of content items for the message
    """
    content = []

    if image is not None and (not isinstance(image, list) or len(image) > 0):
        image_to_encode = (
            image
            if include_all_images or not isinstance(image, list)
            else image[0]
        )
        base64_data = tensor_to_base64(image_to_encode)
        encoded_images = base64_data if isinstance(base64_data, list) else [base64_data]
        if not include_all_images:
            encoded_images = encoded_images[:1]

        for encoded_image in encoded_images:
            image_url = f"{base64_prefix}{encoded_image}"
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
