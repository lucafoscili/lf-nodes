import torch

# region normalize_input_image
def normalize_input_image(image: list[torch.Tensor] | torch.Tensor):
    """
    Converts an input tensor or list of image tensors into a standardized list of individual image tensors.
    
    This function ensures that:
    
    - A 4D tensor (batch of images) is converted into a list of tensors, each with shape [1, H, W, C].
    - A 3D tensor (single image) is converted into a list with one element, maintaining a batch dimension as [1, H, W, C].
    - A list with only one element is handled as a single batch or image, as applicable.
    - A list of images is returned as-is, with each element assumed to be an individual image tensor.
    
    Parameters:
    image (torch.Tensor or list): Input image(s) as a tensor (3D/4D) or a list.
    
    Returns:
    list: A list of individual image tensors, each with a batch dimension.
    
    Raises:
    ValueError: If the input tensor is neither 3D nor 4D.
    """
    if isinstance(image, torch.Tensor):
        if len(image.shape) == 4:
            return [img.unsqueeze(0) for img in image]
        elif len(image.shape) == 3:
            return [image.unsqueeze(0)]
        else:
            raise ValueError("Input tensor must be either 3D or 4D.")
    elif isinstance(image, list):
        if len(image) == 1 and isinstance(image[0], torch.Tensor):
            return normalize_input_image(image[0])
        return image
    else:
        raise TypeError("Input must be a torch.Tensor or list.")
# endregion