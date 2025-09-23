import numpy as np
import torch

# region tensor_to_numpy
def tensor_to_numpy(image: torch.Tensor, threeD: bool = False, dtype: type = np.uint8) -> np.ndarray:
    """
    Convert a tensor to a NumPy array for OpenCV processing.
    
    Args:
        image (torch.Tensor): 4D (1, H, W, C) or 3D (H, W, C) tensor.
        threeD (bool): If True, returns a 3D array (H, W, C).
        dtype (type): Desired NumPy array data type. Defaults to np.uint8.
    
    Returns:
        np.ndarray: Converted NumPy array in the specified data type.
    """
    if image.dim() == 4:
        if image.shape[0] != 1:
            raise ValueError(f"Expected batch size of 1, but got shape {image.shape}")
        image = image.squeeze(0) if not threeD else image[0]
    elif image.dim() != 3:
        raise ValueError(f"Unexpected tensor shape for conversion: {image.shape}")

    try:
        if dtype == np.uint8:
            clamped_image = torch.clamp(image, 0.0, 1.0)
            numpy_array = (clamped_image.cpu().numpy() * 255).astype(dtype)        
        elif dtype == np.float32 or dtype == np.float64:
            numpy_array = image.cpu().numpy().astype(dtype)
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")

        return numpy_array
    except Exception as e:
        print(f"Error converting tensor to NumPy array: {e}")
        raise
# endregion