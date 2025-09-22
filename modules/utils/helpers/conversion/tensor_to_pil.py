import torch

from PIL import Image

from ..conversion import tensor_to_numpy

# region tensor_to_pil
def tensor_to_pil(tensor: torch.Tensor):
    """
    Convert a tensor to a PIL Image.
    
    Args:
        tensor (torch.Tensor): Image tensor, 4D [B, H, W, C] or 3D [H, W, C].
    Returns:
        PIL.Image: Converted PIL image.
    """
    try:
        numpy_image = tensor_to_numpy(tensor, threeD=True)
        return Image.fromarray(numpy_image)
    except Exception as e:
        print(f"Error converting tensor to PIL image: {e}")
        raise
# endregion