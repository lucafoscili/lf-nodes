from folder_paths import get_filename_list

# region get_comfy_list
def get_comfy_list(folder: str):
    """
    Retrieve a list of filenames from a specified folder.

    This function is a wrapper around `get_filename_list` from the `folder_paths` module.
    It retrieves and returns a list of filenames for different types of folders used in the ComfyUI project.

    Args:
        folder (str): The type of folder to retrieve filenames from. Can be one of:
            - "checkpoints": For model checkpoint files
            - "embeddings": For embedding files
            - "loras": For LoRA (Low-Rank Adaptation) files
            - "upscale_models": For upscale models
            - "vae": For VAEs
            - Other folder types as defined in the project structure

    Returns:
        list[str]: A list of filenames in the specified folder.

    Notes:
        - The function uses caching mechanisms to improve performance for repeated calls.
        - It handles legacy folder mappings and ensures consistent behavior across different project versions.
        - The returned list contains only the filenames, without full paths.

    Examples:
        >>> CHECKPOINTS = get_list("checkpoints")
        >>> EMBEDDINGS = get_list("embeddings")
        >>> LORAS = get_list("loras")
    """    
    return get_filename_list(folder)
# endregion