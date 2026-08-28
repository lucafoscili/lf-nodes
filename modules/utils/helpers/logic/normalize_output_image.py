import torch

# region normalize_output_image
def normalize_output_image(image_input):
    """
    Normalize the given image input into both batch and list formats.

    This function handles images of varying resolutions by grouping them into batches
    based on their [H, W] dimensions. It outputs:
    - A list of batch tensors with shape [B, H, W, C], one for each unique resolution.
    - A list of individual image tensors with shape [1, H, W, C].

    Parameters:
    image_input (torch.Tensor or list): The image input to be normalized. It can be:
        - A single tensor [1, H, W, C]
        - A batch tensor [B, H, W, C]
        - A list of individual tensors or batch tensors

    Returns:
    tuple: A tuple containing:
        - batch_list (list): A list of tensors, each with shape [B, H, W, C] for a unique resolution.
        - image_list (list): A list of tensors with shape [1, H, W, C], preserving the batch dimension.
    """
    image_list = []

    def append_tensor(image, label):
        if not isinstance(image, torch.Tensor):
            raise TypeError(f"{label} must be a torch.Tensor.")
        if image.ndim == 4:
            if image.shape[0] < 1:
                raise ValueError(f"{label} batch must contain at least one image.")
            if image.shape[1] < 1 or image.shape[2] < 1:
                raise ValueError(f"{label} image dimensions must be positive.")
            if image.shape[3] not in (3, 4):
                raise ValueError(
                    f"{label} must use RGB or RGBA channels; got {tuple(image.shape)}."
                )
            for item in image:
                image_list.append(item.unsqueeze(0).contiguous())
            return
        if image.ndim == 3:
            if image.shape[0] < 1 or image.shape[1] < 1:
                raise ValueError(f"{label} image dimensions must be positive.")
            if image.shape[2] not in (3, 4):
                raise ValueError(
                    f"{label} must use RGB or RGBA channels; got {tuple(image.shape)}."
                )
            image_list.append(image.unsqueeze(0).contiguous())
            return
        raise ValueError(
            f"{label} must have shape [H,W,C] or [B,H,W,C]; got {tuple(image.shape)}."
        )

    if isinstance(image_input, (list, tuple)):
        if not image_input:
            raise ValueError("Image input is empty.")
        for index, image in enumerate(image_input):
            append_tensor(image, f"image_input[{index}]")
    else:
        append_tensor(image_input, "image_input")

    resolution_groups = {}
    for img in image_list:
        _, h, w, channels = img.shape
        key = (h, w, channels, img.dtype, str(img.device))
        resolution_groups.setdefault(key, []).append(img)

    batch_list = []
    for _, imgs in resolution_groups.items():
        if len(imgs) > 1:
            batch_list.append(torch.cat(imgs, dim=0))
        else:
            batch_list.append(imgs[0])

    return batch_list, image_list
# endregion
