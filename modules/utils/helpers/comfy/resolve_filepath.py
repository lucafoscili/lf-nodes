import os
import torch

from folder_paths import get_save_image_path
from .get_comfy_dir import get_comfy_dir
from ..logic import normalize_list_to_value
from ..temp_cache import TempFileCache

from ....utils.constants import USER_FOLDER

# region resolve_filepath
def resolve_filepath(
        filename_prefix: str = None,
        base_output_path: str = None,
        add_timestamp: bool = False,
        extension: str = "PNG",
        add_counter: bool = True,
        image: torch.Tensor = None,
        temp_cache: TempFileCache = None) -> tuple[str, str, str]:
    """
    Resolve and prepare a file path for saving an image produced by ComfyUI.
    This function builds a full output file path (and related metadata) from a
    filename prefix and an output directory, optionally adding a timestamp token
    and a numeric counter to avoid name collisions. It also infers image
    dimensions from a torch.Tensor (if provided), creates the destination
    directory, and optionally records the path in a temporary cache.

    Parameters:
    - filename_prefix (str | list[str] | None): Base name or prefix for the output
        file. If None, defaults to "<USER_FOLDER>/ComfyUI". Lists are normalized via
        normalize_list_to_value before use.
    - base_output_path (str | None): Directory to place the output file. If None,
        defaults to the ComfyUI temp directory returned by get_comfy_dir("temp").
    - add_timestamp (bool): If True, appends a timestamp pattern
        "_%year%-%month%-%day%_%hour%-%minute%-%second%" to the filename_prefix.
    - extension (str): File extension (without leading dot). Defaults to "PNG".
    - add_counter (bool): If True, appends a numeric counter ("_N") to the
        filename and increments it until an unused filename is found. If False, the
        function will not add or check a counter and will use the provided filename.
    - image (torch.Tensor | any): Optional image used to infer dimensions. If the
        provided value (after normalize_list_to_value) is a torch.Tensor, height and
        width are taken from image.shape[1] and image.shape[2] respectively. If not
        a tensor or not provided, dimensions are passed as None to the path resolver.
    - temp_cache (TempFileCache | None): Optional cache object. If provided, the
        resolved output file path is added to the cache via temp_cache.add().

    Returns:
    - tuple[str, str, str]: A 3-tuple containing:
            - output_file: Full path to the resolved output file (including extension).
            - subfolder: The subfolder path returned by get_save_image_path (may be
                empty or relative to base_output_path).
            - filename: The final filename (including extension and any counter).

    Side effects:
    - Ensures the output folder exists (os.makedirs(..., exist_ok=True)).
    - May create or increment a filename counter by checking existing files on
        disk (os.path.exists).
    - If temp_cache is provided, the resolved output_file is added to it.

    Notes:
    - The function relies on external helpers (normalize_list_to_value,
        get_save_image_path, get_comfy_dir) and global USER_FOLDER. Tokens in the
        timestamp pattern are left as literal placeholders ("%year%", etc.) for
        downstream expansion if desired.
    - The function will raise normal filesystem-related exceptions (e.g. OSError)
        if directory creation or file system checks fail. Type-related errors may
        occur if expected helper functions or types (e.g. torch) are not available.

    Example:
    - Typical return value:
            ("/path/to/output/subfolder/prefix_1.PNG", "subfolder", "prefix_1.PNG")
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
    if temp_cache:
        temp_cache.register(output_file)

    os.makedirs(output_folder, exist_ok=True)

    return output_file, subfolder, filename
# endregion
