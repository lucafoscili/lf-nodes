from typing import Dict, Any, Optional

import torch
import torch.nn as nn

# region make_linear
def make_linear(weight: torch.Tensor, bias: torch.Tensor | None) -> nn.Linear:
    """
    Creates a non-trainable nn.Linear layer with the specified weight and optional bias.

    Args:
        weight (torch.Tensor): The weight tensor of shape (out_features, in_features).
        bias (torch.Tensor | None): The bias tensor of shape (out_features), or None if no bias.

    Returns:
        nn.Linear: A linear layer initialized with the provided weight and bias, with gradients disabled.
    """
    out_features, in_features = weight.shape
    lin = nn.Linear(in_features, out_features, bias=bias is not None)
    with torch.no_grad():
        lin.weight.copy_(weight)
        if bias is not None:
            lin.bias.copy_(bias)
    lin.requires_grad_(False)
    return lin
# endregion

# region extract_linear
def extract_linear(sd: Dict[str, torch.Tensor], base_key: str) -> Optional[nn.Linear]:
    """
    Extracts a linear layer (nn.Linear) from a state dictionary using a specified base key.

    Args:
        sd (Dict[str, torch.Tensor]): State dictionary containing model weights.
        base_key (str): Base key to locate the weight and bias tensors.

    Returns:
        Optional[nn.Linear]: An nn.Linear layer constructed from the extracted weight and bias,
        or None if the required weight tensor is missing or not 2-dimensional.
    """
    w_key = base_key + ".weight"
    b_key = base_key + ".bias"
    if w_key not in sd:
        return None
    weight = sd[w_key]
    bias = sd.get(b_key)
    if weight.dim() != 2:
        return None
    return make_linear(weight, bias)
# endregion

# region derive_capabilities
def derive_capabilities(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derives capability information from a parsed configuration dictionary.

    Args:
        parsed (Dict[str, Any]): A dictionary containing configuration parameters
            for a model variant. Expected keys include "vision_dim", "target_dim",
            "proj_k", "proj_v", "unified_proj", and "variant".

    Returns:
        Dict[str, Any]: A dictionary summarizing the capabilities of the variant,
            including:
                - "variant": The variant name (str).
                - "vision_dim": The vision dimension (Any).
                - "target_dim": The target dimension (Any).
                - "has_proj_k": Whether a projection for 'k' exists (bool).
                - "has_proj_v": Whether a projection for 'v' exists (bool).
                - "has_unified_proj": Whether a unified projection exists (bool).
                - "supports_kv_bias": Whether key/value bias is supported (bool).
                - "recommended_strategy": Recommended strategy based on capabilities (str).
    """
    vision_dim = parsed.get("vision_dim")
    target_dim = parsed.get("target_dim")
    has_k = parsed.get("proj_k") is not None
    has_v = parsed.get("proj_v") is not None
    unified = parsed.get("unified_proj") is not None
    supports_kv_bias = bool(has_k or has_v or unified)
    return {
        "variant": parsed.get("variant", "unknown"),
        "vision_dim": vision_dim,
        "target_dim": target_dim,
        "has_proj_k": has_k,
        "has_proj_v": has_v,
        "has_unified_proj": unified,
        "supports_kv_bias": supports_kv_bias,
        "recommended_strategy": "kv_bias_residual" if supports_kv_bias else "concat_token",
    }
# endregion