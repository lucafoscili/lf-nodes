from .normalize_output_mask import normalize_output_mask

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

    if isinstance(image_count, bool) or not isinstance(image_count, int) or image_count < 1:
        raise ValueError("image_count must be a positive integer.")

    _, masks_list = normalize_output_mask(mask_input)

    if len(masks_list) not in (1, image_count):
        raise ValueError(
            f"Mask count mismatch: got {len(masks_list)} mask(s) for {image_count} image(s). "
            "Provide one mask (broadcast) or one per image."
        )

    return masks_list
# endregion
