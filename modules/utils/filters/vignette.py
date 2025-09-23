import numpy as np
import torch

from PIL import Image, ImageFilter

from ...utils.helpers import hex_to_tuple, pil_to_tensor, tensor_to_pil

# region vignette_effect
def vignette_effect(image: torch.Tensor, intensity: float, radius: float, shape: str, color: str = '000000') -> torch.Tensor:
    """
    Apply a vignette effect to an image tensor with a specified color.

    Args:
        image (torch.Tensor): Input image tensor.
        intensity (float): Intensity of the vignette effect (0 to 1).
        radius (float): Size of the vignette effect (0 to 1). Lower values create a smaller vignette.
        shape (str): Shape of the vignette, either 'elliptical' or 'circular'.
        color (str): Color of the vignette effect (hex).

    Returns:
        torch.Tensor: Image tensor with the vignette effect applied.
    """
    pil_image = tensor_to_pil(image).convert('RGB')
    width, height = pil_image.size

    color = hex_to_tuple(color)
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xv, yv = np.meshgrid(x, y)

    distance = np.sqrt(xv**2 + yv**2) if shape == "circular" else np.sqrt((xv * (width / height))**2 + yv**2)
    distance = distance / distance.max()

    vignette_intensity = np.clip(255 * ((distance - radius) / (1 - radius)), 0, 255).astype(np.uint8)
    vignette_mask = Image.fromarray(vignette_intensity, mode='L')

    vignette_mask = vignette_mask.filter(ImageFilter.GaussianBlur(radius=int(min(width, height) * (1 - radius) / 4)))

    overlay = Image.new('RGB', (width, height), color)
    output_image = Image.composite(overlay, pil_image, vignette_mask)
    output_image = Image.blend(pil_image, output_image, intensity)

    return pil_to_tensor(output_image)
# endregion