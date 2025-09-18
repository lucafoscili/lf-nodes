"""IPAdapter weight parsing for SDXL (face-focused variant first).

This module inspects a loaded state_dict and extracts projector layers
for use inside fusion strategies. We begin with SDXL face-style adapters
(plus / plus-face naming) whose weights typically contain linear
projections mapping vision features into the UNet cross-attention space.

Design goals:
- Stateless pure functions returning lightweight CPU nn.Linear layers.
- Graceful fallback: if expected keys missing, return None so caller can
  choose a simpler fusion (e.g., direct pooled token concat).
- Extensible: additional variants register pattern-matchers.

Convention:
Return structure:
{
  "proj_k": nn.Linear | None,
  "proj_v": nn.Linear | None,
  "vision_dim": int,
  "target_dim": int,
  "variant": str,
  "notes": str,
}

We keep linears on CPU; caller moves them to GPU only when first used.
"""
import torch
import torch.nn as nn

from typing import Dict, Optional, Any

from .variants import discover  # dynamic matcher discovery

# region Utility helpers
def _make_linear(weight: torch.Tensor, bias: torch.Tensor | None) -> nn.Linear:
    """
    Creates a non-trainable nn.Linear layer from given weight and bias tensors.

    Args:
        weight (torch.Tensor): The weight tensor of shape (out_features, in_features).
        bias (torch.Tensor | None): The bias tensor of shape (out_features), or None if no bias.

    Returns:
        nn.Linear: A linear layer initialized with the provided weights and bias, with gradients disabled.
    """
    out_features, in_features = weight.shape
    lin = nn.Linear(in_features, out_features, bias=bias is not None)
    with torch.no_grad():
        lin.weight.copy_(weight)
        if bias is not None:
            lin.bias.copy_(bias)
    lin.requires_grad_(False)
    return lin


def _extract_linear(sd: Dict[str, torch.Tensor], base_key: str) -> Optional[nn.Linear]:
    """
    Extracts a linear layer (nn.Linear) from a state dictionary using a specified base key.

    Args:
        sd (Dict[str, torch.Tensor]): State dictionary containing model parameters.
        base_key (str): Base key used to locate the weight and bias tensors in the state dictionary.

    Returns:
        Optional[nn.Linear]: An nn.Linear layer constructed from the extracted weight and bias tensors,
                             or None if the required tensors are not found or have invalid dimensions.
    """
    w_key = base_key + ".weight"
    b_key = base_key + ".bias"
    if w_key not in sd:
        return None
    weight = sd[w_key]
    bias = sd.get(b_key)
    if weight.dim() != 2:
        return None
    return _make_linear(weight, bias)
# endregion

# region Public API
def parse_ipadapter_weights(state_dict: Dict[str, torch.Tensor], meta: Dict[str, Any] | None = None) -> Optional[Dict[str, Any]]:
    """
    Parses IP-Adapter weights from a given state dictionary using available matchers.

    Attempts to match the provided `state_dict` and optional `meta` information against known IP-Adapter weight formats.
    If a matcher successfully parses the weights, its output is returned. If no matcher matches and the filename in `meta`
    suggests a face-related model, a debug summary is added to `meta` for upstream logging.

    Args:
        state_dict (Dict[str, torch.Tensor]): The state dictionary containing model weights.
        meta (Optional[Dict[str, Any]]): Optional metadata, such as filename or additional context.

    Returns:
        Optional[Dict[str, Any]]: Parsed weight information if a matcher succeeds, otherwise None.
    """

    meta = meta or {}
    for matcher in discover():
        try:
            out = matcher(state_dict, meta)
        except Exception:
            continue  # ignore matcher failures
        if out:
            return out
    # Enhanced debug for face-related filenames when no variant matched.
    fname = (meta.get("filename") or "").lower()
    if any(tag in fname for tag in ("face", "faceid", "plus")):
        # Provide a lightweight introspection structure for logging upstream.
        sample_keys = list(state_dict.keys())[:12]
        dims_summary = {}
        for k, v in list(state_dict.items())[:50]:  # cap scanning
            if hasattr(v, "shape") and getattr(v, "dim", lambda: 0)() == 2:
                dims_summary.setdefault(tuple(v.shape), 0)
                dims_summary[tuple(v.shape)] += 1
        meta.setdefault("unrecognized_debug", {
            "sample_keys": sample_keys,
            "linear_shape_counts": {f"{k}": c for k, c in list(dims_summary.items())[:8]},
            "total_tensors": len(state_dict),
        })
    return None
# endregion
