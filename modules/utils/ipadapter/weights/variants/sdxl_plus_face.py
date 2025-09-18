import re
import torch

from typing import Dict, Any, Optional, List

from .base import extract_linear, derive_capabilities

def _match_sdxl_plus_face(sd: Dict[str, torch.Tensor], meta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Attempts to heuristically match and extract the key and value projection layers ("proj_k" and "proj_v")
    from a given state dictionary for SDXL plus/face adapter weights.

    The function searches for keys related to "proj_k" and "proj_v" using regular expressions, and if not found,
    falls back to selecting the first two compatible linear layers based on their shapes. It then extracts these
    layers and returns a dictionary containing the extracted layers, their input and output dimensions, variant
    information, notes, and derived capabilities.

    Args:
        sd (Dict[str, torch.Tensor]): State dictionary containing model weights.
        meta (Dict[str, Any]): Metadata associated with the weights.

    Returns:
        Optional[Dict[str, Any]]: A dictionary with extracted projection layers and related information if a match
        is found; otherwise, None.
    """
    joined_keys = " ".join(sd.keys())
    if not ("ip" in joined_keys and ("proj" in joined_keys or "adapter" in joined_keys)):
        return None
    k_key = None
    v_key = None
    for key in sd.keys():
        if re.search(r"proj[_\.]*k", key):
            k_key = key.rsplit(".weight", 1)[0] if key.endswith(".weight") else key
        if re.search(r"proj[_\.]*v", key):
            v_key = key.rsplit(".weight", 1)[0] if key.endswith(".weight") else key
    proj_k = extract_linear(sd, k_key) if k_key else None
    proj_v = extract_linear(sd, v_key) if v_key else None
    if proj_k is None or proj_v is None:
        # fallback heuristic: choose first two compatible linears
        candidate: List[str] = []
        for k, t in sd.items():
            if k.endswith('.weight') and t.dim()==2 and t.shape[1] in (768,1024,1280) and t.shape[0] in (768,1024,1280,2048):
                candidate.append(k.rsplit('.weight',1)[0])
                if len(candidate) >= 2:
                    break
        if len(candidate) >= 2:
            if proj_k is None:
                proj_k = extract_linear(sd, candidate[0])
            if proj_v is None:
                proj_v = extract_linear(sd, candidate[1])
    if proj_k is None and proj_v is None:
        return None
    vision_dim = proj_k.in_features if proj_k else proj_v.in_features
    target_dim = proj_k.out_features if proj_k else proj_v.out_features
    parsed = {
        "proj_k": proj_k,
        "proj_v": proj_v,
        "vision_dim": vision_dim,
        "target_dim": target_dim,
        "variant": "sdxl_plus_face",
        "notes": "Heuristic match for SDXL plus/face adapter.",
    }
    capabilities = derive_capabilities(parsed)
    parsed["capabilities"] = capabilities
    return parsed

def register():
    """
    Registers the SDXL Plus Face variant matcher.

    Returns:
        list: A list containing the `_match_sdxl_plus_face` matcher function.
    """
    return [_match_sdxl_plus_face]
