from __future__ import annotations
from typing import List

import torch

from ..api import get_resource_url
from ..comfy import resolve_filepath
from ..conversion import tensor_to_pil
from ..ui import create_compare_node

# region append_compare_entry
def append_compare_entry(
    original: torch.Tensor,
    overlay: torch.Tensor,
    nodes: List[dict],
    index: int,
) -> None:
    """
    Saves the original and overlay image tensors as PNG files, generates resource URLs for each,
    and appends a comparison node to the provided nodes list.

    Args:
        original (torch.Tensor): The original image tensor to be saved and compared.
        overlay (torch.Tensor): The overlay image tensor to be saved and compared.
        nodes (List[dict]): The list of comparison nodes to which a new entry will be appended.
        index (int): The index used for the comparison node.

    Returns:
        None
    """    
    orig_path, orig_sub, orig_name = resolve_filepath("detect_regions_orig", image=original)
    tensor_to_pil(original).save(orig_path, "PNG")

    overlay_path, overlay_sub, overlay_name = resolve_filepath("detect_regions_overlay", image=overlay)
    tensor_to_pil(overlay).save(overlay_path, "PNG")

    url_before = get_resource_url(orig_sub, orig_name, "temp")
    url_after = get_resource_url(overlay_sub, overlay_name, "temp")
    nodes.append(create_compare_node(url_before, url_after, index))
# endregion