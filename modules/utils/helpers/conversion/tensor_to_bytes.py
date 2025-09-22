import io
import torch

from PIL import Image

from ..conversion import tensor_to_numpy

# region tensor_to_bytes
def tensor_to_bytes(tensor: torch.Tensor, format: str):
    """
    Convert a tensor to image bytes (JPEG or PNG).
    
    Args:
        tensor (torch.Tensor): Image tensor, 4D [B, H, W, C] or 3D [H, W, C].
        format (str): Desired image format (e.g., "JPEG", "PNG").
    """
    numpy_image = tensor_to_numpy(tensor, threeD=True)
    img = Image.fromarray(numpy_image)
    
    buffer = io.BytesIO()
    img.save(buffer, format)
    return buffer.getvalue()
# endregion