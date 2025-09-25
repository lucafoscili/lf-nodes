import torch

# region normalize_masks_for_images
def normalize_masks_for_images(mask_input, image_count: int) -> list:
    """
    Normalize mask input (single mask, list/tuple, or batched tensor) into a list matching image count.

    Allows a single mask to be broadcast across all images.

    Parameters:
        mask_input: A single mask tensor, list/tuple of masks, or batched mask tensor.
        image_count (int): Number of images that masks should align with.

    Returns:
        list: A list of masks aligned with the number of images.

    Raises:
        ValueError: If no mask is provided or the mask count does not match image_count.
    """
    if mask_input is None:
        raise ValueError("Mask is required for inpaint filter node.")

    masks_list: list

    if isinstance(mask_input, (list, tuple)):
        masks_list = list(mask_input)
    elif torch.is_tensor(mask_input):
        try:
            if mask_input.dim() >= 3 and mask_input.shape[0] == image_count:
                masks_list = [mask_input[i : i + 1].contiguous() for i in range(image_count)]
            else:
                masks_list = [mask_input]
        except Exception:
            masks_list = [mask_input]
    else:
        masks_list = [mask_input]

    if len(masks_list) not in (1, image_count):
        raise ValueError(
            f"Mask count mismatch: got {len(masks_list)} mask(s) for {image_count} image(s). "
            "Provide one mask (broadcast) or one per image."
        )

    return masks_list
# endregion
