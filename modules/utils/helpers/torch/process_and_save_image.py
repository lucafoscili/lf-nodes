import torch

from ..ui import cache_generated_preview, create_compare_node

# region process_and_save_image
def process_and_save_image(
    images: list[torch.Tensor],
    filter_function: callable,
    filter_args: dict,
    nodes: list[dict],
):
    """
    Processes a list of images using a specified filter function, saves both the original and processed images to disk,
    and appends comparison nodes to the provided nodes list.
    Args:
        images (list[torch.Tensor]): List of image tensors to process.
        filter_function (callable): Function to apply to each image tensor for processing.
        filter_args (dict): Dictionary of arguments to pass to the filter function.
        nodes (list[dict]): List to which comparison nodes will be appended.
    Returns:
        list[torch.Tensor]: List of processed image tensors.
    """
    processed_images = []

    for index, img in enumerate(images):
        source_preview = cache_generated_preview(img)
        alpha = img[..., 3:4] if img.shape[-1] == 4 else None
        filter_input = img[..., :3] if alpha is not None else img
        processed = filter_function(filter_input, **filter_args)

        if not isinstance(processed, torch.Tensor) or processed.ndim != 4:
            raise ValueError("Image filters must return a 4-D BHWC tensor.")
        if processed.shape[:3] != img.shape[:3]:
            raise ValueError(
                "Image filters must preserve batch and spatial dimensions; "
                f"got {tuple(processed.shape)} for input {tuple(img.shape)}."
            )
        if processed.shape[-1] not in (3, 4):
            raise ValueError("Image filters must return RGB or RGBA pixels.")

        if alpha is not None:
            processed = torch.cat(
                (
                    processed[..., :3],
                    alpha.to(device=processed.device, dtype=processed.dtype),
                ),
                dim=-1,
            )
        target_preview = cache_generated_preview(processed)

        nodes.append(
            create_compare_node(source_preview.url, target_preview.url, index)
        )
        processed_images.append(processed)

    return processed_images
# endregion
