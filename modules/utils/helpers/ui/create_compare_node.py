# region create_compare_node
def create_compare_node(before: str, after: str, index: int):
    """
    Create a comparison node dictionary using the provided before and after image paths.

    Args:
        before (str): Path to the first image (before comparison). 
        after (str): Path to the second image (after comparison).
        index (int): Index value for the node.

    Returns:
        dict: A dictionary representing the comparison node.
    """
    node = {
        "cells": {
            "lfImage": {"shape": "image", "lfValue": f"{before}", "value": ''},
            "lfImage_after": {"shape": "image", "lfValue": f"{after}", "value": ''}
        },
        "id": f"image_{index+1}",
        "value": f"Comparison {index+1}"
    }
    return node
# endregion