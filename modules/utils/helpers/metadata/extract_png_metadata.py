# region extract_png_metadata
def extract_png_metadata(pil_image):
    """
    Extract metadata from a PNG image using a PIL Image object.

    Args:
        pil_image (PIL.Image): The PIL image object containing the PNG image data.

    Returns:
        dict: A dictionary containing PNG metadata as key-value pairs.
    """
    png_info = pil_image.info
    metadata = {}

    for key, value in png_info.items():
        if isinstance(value, str):
            metadata[key] = value

    return metadata
# endregion