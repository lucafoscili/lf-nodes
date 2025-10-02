import torch

# region normalize_input_image
def normalize_input_image(image):
    """Convert arbitrary image containers into a flat list of `[1, H, W, C]` tensors.

    Accepts tensors, lists, or tuples (including arbitrarily nested combinations) and
    returns a list where every element keeps an explicit batch dimension of size 1.

    Parameters:
        image: torch.Tensor | list | tuple | None

    Returns:
        list[torch.Tensor]: list of tensors with shape `[1, H, W, C]`.

    Raises:
        ValueError: if tensors do not have 3 or 4 dimensions.
        TypeError: if unsupported types are encountered.
    """

    if image is None:
        return []

    flat_images: list[torch.Tensor] = []

    def _collect(item):
        if item is None:
            return
        if isinstance(item, torch.Tensor):
            if item.dim() == 4:
                if item.shape[0] == 1:
                    flat_images.append(item)
                else:
                    for single in item:
                        flat_images.append(single.unsqueeze(0))
            elif item.dim() == 3:
                flat_images.append(item.unsqueeze(0))
            else:
                raise ValueError(f"Input tensor must be 3D or 4D. Got shape {tuple(item.shape)}")
        elif isinstance(item, (list, tuple)):
            for sub_item in item:
                _collect(sub_item)
        else:
            raise TypeError(f"Unsupported image container type: {type(item)}")

    _collect(image)

    return flat_images
# endregion