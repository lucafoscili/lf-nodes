import base64
import io
import torch

from PIL import Image

from .tensor_to_numpy import tensor_to_numpy

# region tensor_to_base64
def tensor_to_base64(tensors: list[torch.Tensor] | torch.Tensor):
    """
    Convert PyTorch tensor(s) to base64 encoding.
    
    Args:
        tensors (torch.Tensor or List[torch.Tensor]): Image tensor(s).
    Returns:
        str or List[str]: Base64 encoded string(s) of tensor images.
    """
    def convert_single_tensor(tensor: torch.Tensor):
        if len(tensor.shape) == 4:
            tensor = tensor[0]  # Take the first image in the batch
        if tensor.shape[-1] != 3:
            tensor = tensor[:, :, :3]  # Limit to 3 channels if necessary
        
        # Use tensor_to_numpy to get the numpy array, then convert to PIL
        numpy_image = tensor_to_numpy(tensor, threeD=True)
        pil_img = Image.fromarray(numpy_image)
        
        buffer = io.BytesIO()
        pil_img.save(buffer, format="png", quality=60)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    if isinstance(tensors, list):
        return [convert_single_tensor(tensor) for tensor in tensors]
    return convert_single_tensor(tensors)
# endregion