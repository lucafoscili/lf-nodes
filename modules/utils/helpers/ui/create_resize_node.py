# region create_resize_node
def create_resize_node(height_s: int, width_s: int, height_t: int, width_t: int, index: int):
    """
    Create a resize node containing image dimension change information.

    Args:
        height_s (int): Source image height.
        width_s (int): Source image width.
        height_t (int): Target image height after resizing.
        width_t (int): Target image width after resizing.
        index (int): The index identifier for the node.

    Returns:
        dict: A dictionary representing the resize operation for an image.
    """
    node = {
        "id": f"{index}", "value": f"[{index}] From {height_s}x{width_s} to {height_t}x{width_t}"
    }
    return node
# endregion