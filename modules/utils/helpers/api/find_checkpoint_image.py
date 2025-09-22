import os

# region find_checkpoint_image
def find_checkpoint_image(checkpoint_path):
    """
    Locate an image file associated with a checkpoint by trying multiple common file extensions.

    Args:
        checkpoint_path (str): The file path of the checkpoint, without extension.

    Returns:
        str or None: The path of the found image file; None if not found.
    """
    extensions = ["jpg", "jpeg", "JPEG", "png", "webp", "WEBP"]

    for ext in extensions:
        image_path = f"{os.path.splitext(checkpoint_path)[0]}.{ext}"
        if os.path.exists(image_path):
            return image_path
    return None
# endregion