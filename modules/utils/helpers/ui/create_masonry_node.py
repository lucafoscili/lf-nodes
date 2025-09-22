# region create_masonry_node
def create_masonry_node(filename: str, url: str, index: int):
    """
    Create a masonry node representation for images.

    Args:
        filename (str): The filename to use for the image's identifier and title.
        url (str): The URL path to the image resource.
        index (int): The index to generate a unique node ID.

    Returns:
        dict: A dictionary containing image node details.
    """
    node = {
        "cells": {
            "lfImage": {"htmlProps":{"id": filename, "title": filename}, "shape": "image", "lfValue": f"{url}", "value": f"{url}"}
        },
        "id": f"{index+1}",
        "value": f"{index+1}"
    }
    return node
# endregion