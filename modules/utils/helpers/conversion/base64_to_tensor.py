import base64
import io
import numpy as np
import torch

from PIL import Image

# region base64_to_tensor
def base64_to_tensor(base64_str: str, preserve_alpha = False) -> torch.Tensor:
    """
    Convert a base64-encoded image string to a PyTorch tensor in [B, H, W, C] format.

    Args:
        base64_str (str): The base64 encoded image string.
        preserve_alpha (bool): If True, preserve the alpha channel (output is RGBA).
                               If False, fallback to RGB by removing or converting the alpha channel.

    Returns:
        torch.Tensor: A PyTorch tensor with shape [B, H, W, C], where B is the batch size.
    """
    if base64_str.startswith("data:image/"):
        base64_str = base64_str.split(",")[1]

    image_data = base64.b64decode(base64_str)
    
    buffer = io.BytesIO(image_data)
    pil_img = Image.open(buffer)

    if preserve_alpha:
        pil_img = pil_img.convert('RGBA')
    else:
        pil_img = pil_img.convert('RGB')

    img_array = np.asarray(pil_img) / 255.0

    img_tensor = torch.from_numpy(img_array).float()  # Shape: [H, W, C]

    if not preserve_alpha:
        if img_tensor.ndim == 2:
            img_tensor = img_tensor.unsqueeze(-1).repeat(1, 1, 3)
        elif img_tensor.shape[-1] == 1:
            img_tensor = img_tensor.repeat(1, 1, 3)

    img_tensor = img_tensor.unsqueeze(0)

    return img_tensor
# endregion