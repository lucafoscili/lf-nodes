from __future__ import annotations

from typing import  List, Optional

# region select_region
def select_region(
    regions: List[dict],
    select_index: int,
    strategy: str,
    preferred_label: Optional[str],
) -> Optional[dict]:
    """
    Selects a region from a list of region dictionaries based on a selection strategy.

    The selection follows this priority:
    1. If `preferred_label` is provided, returns the first region with a matching label (case-insensitive).
    2. If `select_index` is a valid index, returns the region at that index.
    3. Otherwise, selects the region with the maximum value of either 'area' or 'confidence', depending on `strategy`.

    The selected region is annotated with a 'selection_reason' key indicating the reason for selection.

    Args:
        regions (List[dict]): List of region dictionaries, each containing region attributes.
        select_index (int): Index of the region to select if valid (>= 0 and within bounds).
        strategy (str): Selection strategy, either 'area' or 'confidence'.
        preferred_label (Optional[str]): Preferred label to match for selection.

    Returns:
        Optional[dict]: The selected region dictionary, or None if no regions are available.
    """    
    if not regions:
        return None

    if preferred_label:
        for region in regions:
            label = (region.get("label") or "").lower()
            if label == preferred_label:
                region["selection_reason"] = "preferred_label"
                return region

    if select_index >= 0:
        if select_index < len(regions):
            region = regions[select_index]
            region["selection_reason"] = "index"
            region["selection_index"] = select_index
            return region

    metric = "area" if strategy == "area" else "confidence"
    region = max(regions, key=lambda item: float(item.get(metric, 0.0)))
    region["selection_reason"] = metric
    
    return region
# endregion