from __future__ import annotations
from typing import List

import torch

from ..temp_cache import TempFileCache
from ..ui import cache_generated_preview, create_compare_node

# region append_compare_entry
def append_compare_entry(
    original: torch.Tensor,
    overlay: torch.Tensor,
    nodes: List[dict],
    index: int,
    temp_cache: TempFileCache | None = None,
) -> None:
    """
    Saves the original and overlay image tensors as PNG files, generates resource URLs for each,
    and appends a comparison node to the provided nodes list.

    Args:
        original (torch.Tensor): The original image tensor to be saved and compared.
        overlay (torch.Tensor): The overlay image tensor to be saved and compared.
        nodes (List[dict]): The list of comparison nodes to which a new entry will be appended.
        index (int): The index used for the comparison node.
        temp_cache (TempFileCache): Deprecated compatibility parameter. Generated
            previews now live in LF's restart-stable managed preview cache.

    Returns:
        None
    """    
    del temp_cache
    original_preview = cache_generated_preview(original)
    overlay_preview = cache_generated_preview(overlay)
    nodes.append(
        create_compare_node(original_preview.url, overlay_preview.url, index)
    )
# endregion
