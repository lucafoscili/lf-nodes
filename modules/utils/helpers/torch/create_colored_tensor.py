import torch

from ..conversion import hex_to_tuple

# region create_colored_tensor
def create_colored_tensor(input_tensor: torch.Tensor, hex_color: str = None) -> torch.Tensor:
    """
    Creates a tensor with the same shape as `input_tensor`, filled with the specified color.
    
    Args:
        input_tensor (torch.Tensor): A tensor of shape [1, H, W, C], where C is 3 or 4.
        hex_color (str, optional): Hexadecimal color string (e.g., '#RRGGBB' or '#RRGGBBAA'). 
                                   If not provided, defaults to black for 3 channels or transparent for 4 channels.
                                   
    Returns:
        torch.Tensor: A tensor of shape [1, H, W, C] filled with the specified color.
    
    Raises:
        TypeError: If `input_tensor` is not a torch.Tensor.
        ValueError: If `input_tensor` does not have shape [1, H, W, C] or if `C` is not 3 or 4.
                    Also raised if `hex_color` is not in the correct format.
    """
    if not isinstance(input_tensor, torch.Tensor):
        raise TypeError("`input_tensor` must be a torch.Tensor.")
    
    if input_tensor.ndim != 4 or input_tensor.shape[0] != 1:
        raise ValueError("`input_tensor` must have shape [1, H, W, C].")
    
    C = input_tensor.shape[-1]
    if C not in [3, 4]:
        raise ValueError("The channel dimension `C` must be either 3 or 4.")
    
    if hex_color is not None:
        color = hex_to_tuple(hex_color)
    else:
        color = [0, 0, 0] if C == 3 else [0, 0, 0, 0]
    
    if input_tensor.dtype.is_floating_point:
        color = [c / 255.0 for c in color]
    else:
        color = [c for c in color]
    
    H, W = input_tensor.shape[1], input_tensor.shape[2]
    color_tensor = torch.tensor(color, dtype=input_tensor.dtype, device=input_tensor.device)
    color_tensor = color_tensor.view(1, 1, 1, C).expand(1, H, W, C)
    
    return color_tensor
# endregion