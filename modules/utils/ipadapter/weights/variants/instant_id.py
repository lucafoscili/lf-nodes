import torch

from typing import Dict, Any, Optional

from .base import extract_linear, derive_capabilities

# Stub matcher for instant_id variant (placeholder heuristic)
# This will be refined once real key patterns are confirmed.

def _match_instant_id(sd: Dict[str, torch.Tensor], meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Attempts to heuristically identify and extract parameters for an 'instant_id' adapter variant from the given state dictionary.

    The function checks the provided metadata for a filename indicating an 'instant_id' variant. If found, it searches the state dictionary
    for a single linear projection layer that maps from a vision dimension (512, 768, or 1024) to a target dimension (768, 1024, or 1280).
    If such a layer is found, its parameters are extracted and returned in a structured dictionary, along with inferred capabilities.

    Args:
        sd (Dict[str, torch.Tensor]): State dictionary containing model weights.
        meta (Dict[str, Any]): Metadata dictionary, expected to contain a 'filename' key.

    Returns:
        Optional[Dict[str, Any]]: A dictionary with extracted adapter parameters and capabilities if a match is found, otherwise None.
    """
    fname = (meta.get("filename") or "").lower()
    if "instant" not in fname and "instant_id" not in fname:
        return None
    # Heuristic: try to find a single projection that maps 512->hidden or hidden->hidden
    unified = None
    for k, t in sd.items():
        if k.endswith('.weight') and t.dim()==2 and (t.shape[1] in (512,768,1024) and t.shape[0] in (768,1024,1280)):
            unified = extract_linear(sd, k.rsplit('.weight',1)[0])
            break
    if unified is None:
        return None
    parsed = {
        "unified_proj": unified,
        "vision_dim": unified.in_features,
        "target_dim": unified.out_features,
        "variant": "instant_id_sdxl",
        "notes": "Heuristic match for instant_id adapter (placeholder).",
    }
    capabilities = derive_capabilities(parsed)
    parsed["capabilities"] = capabilities
    return parsed

def register():
    """
    Registers and returns a list containing the `_match_instant_id` function.

    Returns:
        list: A list with the `_match_instant_id` function as its only element.
    """
    return [_match_instant_id]
