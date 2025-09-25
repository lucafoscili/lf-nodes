import torch

from ..api import get_resource_url
from ..comfy import resolve_filepath
from ..conversion import tensor_to_pil
from ..ui import create_compare_node

# region process_and_save_image
def process_and_save_image(
    images: list[torch.Tensor],
    filter_function: callable,
    filter_args: dict,
    filename_prefix: str,
    nodes: list[dict],
):
    """
    Processes a list of images using a specified filter function, saves both the original and processed images to disk,
    and appends comparison nodes to the provided nodes list.
    Args:
        images (list[torch.Tensor]): List of image tensors to process.
        filter_function (callable): Function to apply to each image tensor for processing.
        filter_args (dict): Dictionary of arguments to pass to the filter function.
        filename_prefix (str): Prefix to use for saved image filenames.
        nodes (list[dict]): List to which comparison nodes will be appended.
    Returns:
        list[torch.Tensor]: List of processed image tensors.
    """
    processed_images = []
    
    for index, img in enumerate(images):
        pil_image = tensor_to_pil(img)
        output_file_s, subfolder_s, filename_s = resolve_filepath(
            filename_prefix=f"{filename_prefix}_s",
            image=img,
        )
        pil_image.save(output_file_s, format="PNG")
        filename_s = get_resource_url(subfolder_s, filename_s, "temp")

        processed = filter_function(img, **filter_args)

        pil_image = tensor_to_pil(processed)
        output_file_t, subfolder_t, filename_t = resolve_filepath(
            filename_prefix=f"{filename_prefix}_t",
            image=processed,
        )
        pil_image.save(output_file_t, format="PNG")
        filename_t = get_resource_url(subfolder_t, filename_t, "temp")

        nodes.append(create_compare_node(filename_s, filename_t, index))
        processed_images.append(processed)

    return processed_images
# endregion