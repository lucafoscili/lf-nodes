import torch


def _normalize_image_tensor(item: torch.Tensor) -> torch.Tensor:
    """Validate one IMAGE tensor and return canonical BHWC storage."""

    if item.dim() == 3:
        item = item.unsqueeze(0)
    elif item.dim() != 4:
        raise ValueError(
            f"Input tensor must be 3D or 4D. Got shape {tuple(item.shape)}"
        )

    if item.shape[0] < 1:
        raise ValueError("Input image batch must contain at least one image.")
    if item.shape[1] < 1 or item.shape[2] < 1:
        raise ValueError("Input image dimensions must be positive.")
    if item.shape[3] not in (3, 4):
        raise ValueError(
            "Input images must use RGB or RGBA channels; "
            f"got shape {tuple(item.shape)}."
        )
    return item.contiguous()


def normalize_input_image_batches(image):
    """Flatten containers while preserving every coherent IMAGE batch.

    This is the batch-aware companion to :func:`normalize_input_image`.  Use it
    when a model (for example a temporal VAE) assigns meaning to samples being
    decoded or encoded together.  Nested containers are flattened, but an
    incoming ``[B,H,W,C]`` tensor remains one tensor with the same ``B``.
    """

    if image is None:
        return []

    batches: list[torch.Tensor] = []

    def _collect(item):
        if item is None:
            return
        if isinstance(item, torch.Tensor):
            batches.append(_normalize_image_tensor(item))
        elif isinstance(item, (list, tuple)):
            for sub_item in item:
                _collect(sub_item)
        else:
            raise TypeError(f"Unsupported image container type: {type(item)}")

    _collect(image)
    return batches

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
            batch = _normalize_image_tensor(item)
            if batch.shape[0] == 1:
                flat_images.append(batch)
            else:
                for single in batch:
                    flat_images.append(single.unsqueeze(0).contiguous())
        elif isinstance(item, (list, tuple)):
            for sub_item in item:
                _collect(sub_item)
        else:
            raise TypeError(f"Unsupported image container type: {type(item)}")

    _collect(image)

    return flat_images
# endregion
