import os
import torch

from folder_paths import get_save_image_path
from .get_comfy_dir import get_comfy_dir
from ..logic import normalize_list_to_value

from ....utils.constants import USER_FOLDER

# region resolve_filepath
def resolve_filepath(filename_prefix: str = None, base_output_path: str = None, add_timestamp: bool = False, extension: str = "PNG", add_counter: bool = True, image: torch.Tensor = None) -> str:
    """
    Simplified helper function using ComfyUI's core image-saving logic, ensuring folder and filename separation.
    
    Parameters:
        filepath (str or list): Target file path or list of paths. Uses filepath[count] or defaults to the first item if it's a list.
        base_output_path (str): Base directory path to prepend if not specified in filepath.
        index (int): Index for filepath when it's a list. Defaults to 0.
        add_timestamp (bool): Appends a timestamp to the filename if True. Defaults to False.
        default_filename (str): Default filename if filepath lacks one. Defaults to "ComfyUI".
        extension (str): File extension, such as 'png' or 'jpeg'. Defaults to 'json'.
        add_counter (bool): Adds counter as a suffix.

    Returns:
        str: Fully resolved file path with subfolders, filename, and extension.
    """

    if filename_prefix == None:
        filename_prefix = f"{USER_FOLDER}/ComfyUI"
    else:
        filename_prefix = normalize_list_to_value(filename_prefix)

    if base_output_path == None:
        base_output_path = get_comfy_dir("temp")

    if add_timestamp:
        filename_prefix = f"{filename_prefix}_%year%-%month%-%day%_%hour%-%minute%-%second%"
    
    if isinstance(normalize_list_to_value(image), torch.Tensor):
        height = image.shape[1]
        width = image.shape[2]
    else:
        height = None
        width = None

    output_folder, filename, counter, subfolder, _ = get_save_image_path(
        filename_prefix=filename_prefix,
        output_dir=base_output_path,
        image_height=height,
        image_width=width,
    )

    if add_counter:
        while os.path.exists(os.path.join(output_folder, f"{filename}_{counter}.{extension}")):
            counter += 1
        filename = f"{filename}_{counter}.{extension}"
    else:
        filename = f"{filename}.{extension}"

    output_file = os.path.join(output_folder, filename)

    os.makedirs(output_folder, exist_ok=True)

    return output_file, subfolder, filename
# endregion