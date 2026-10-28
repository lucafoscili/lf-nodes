# region create_compare_node
from typing import Optional

def create_compare_node(
    before: str,
    after: str,
    index: int,
    *,
    debug: Optional[str] = None,
    title: Optional[str] = None,
):
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
    
    if title:
        node["value"] = title

    if debug:
        node["cells"]["lfImage_debug"] = {
            "shape": "image",
            "lfValue": f"{debug}",
            "value": ""
        }

    if title:
        # LF Compare flattens image cells; its selector reads cell.value rather
        # than the containing node's title.
        for name, suffix in (("lfImage", "before"), ("lfImage_after", "after"),
                             ("lfImage_debug", "debug")):
            if name in node["cells"]:
                node["cells"][name]["value"] = f"{title} ({suffix})"

    return node
# endregion
