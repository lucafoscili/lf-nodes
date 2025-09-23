import torch

# region numpy_to_tensor
def numpy_to_tensor(numpy_array):
    """
    Convert a NumPy array to a PyTorch tensor.

    Args:
        numpy_array (numpy.ndarray): The input NumPy array representing the image.
            It should be a 2D array with shape [H, W, C] or a 3D array with shape [B, H, W, C].

    Returns:
        torch.Tensor: The converted PyTorch tensor.

    Notes:
        - The tensor values are automatically scaled from [0, 255] to [0, 1].
    """
    try:
        tensor = torch.from_numpy(numpy_array).float() / 255.0

        if tensor.dim() == 3:
            return tensor
        elif tensor.dim() == 4:
            return tensor
        else:
            raise ValueError(f"Unexpected input shape: {tensor.shape}")
    except Exception as e:
        print(f"Error converting NumPy array to tensor: {e}")
        raise
# endregion