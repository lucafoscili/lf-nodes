import torch
from copy import deepcopy
from typing import Any, Dict, Iterable, List

def _flatten_latent_items(latent_input: Any) -> List[Dict[str, Any]]:
    """Recursively collect latent dictionaries from possibly nested lists/tuples."""
    if latent_input is None:
        return []
    if isinstance(latent_input, dict):
        return [latent_input]
    if isinstance(latent_input, (list, tuple)):
        latents: List[Dict[str, Any]] = []
        for item in latent_input:
            latents.extend(_flatten_latent_items(item))
        return latents
    raise TypeError(
        f"Unsupported latent input type: {type(latent_input).__name__}. Expected dict or list of dicts."
    )

def _cat_tensor_sequence(values: Iterable[torch.Tensor]) -> torch.Tensor:
    tensors = []
    for value in values:
        if value is None:
            continue
        if not isinstance(value, torch.Tensor):
            raise TypeError("Expected torch.Tensor when concatenating latent data.")
        if value.dim() == 0:
            tensors.append(value.unsqueeze(0))
        else:
            tensors.append(value)
    if not tensors:
        raise ValueError("No tensors available to concatenate.")
    return torch.cat(tensors, dim=0)

def _merge_optional_tensor_sequence(values: Iterable[Any]) -> Any:
    tensors = [value for value in values if isinstance(value, torch.Tensor)]
    if tensors:
        return _cat_tensor_sequence(tensors)

    sequences: List[int] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            sequences.extend(int(v) for v in value)
        else:
            sequences.append(int(value))
    return sequences or None

def normalize_input_latent(latent_input: Any) -> Dict[str, Any]:
    """
    Normalize latent inputs so downstream nodes always receive a single latent dictionary.

    Accepts a single latent dict, a list/tuple of latent dicts, or nested combinations thereof.
    The "samples" tensor (and other tensor-valued entries such as "noise_mask") are concatenated
    along the batch dimension so the returned dictionary represents the whole batch.
    """
    flattened = _flatten_latent_items(latent_input)
    if not flattened:
        raise ValueError("Latent input is empty. Provide at least one latent sample.")

    if len(flattened) == 1:
        return deepcopy(flattened[0])

    merged: Dict[str, Any] = {}

    sample_tensors = [item.get("samples") for item in flattened]
    if any(tensor is None for tensor in sample_tensors):
        raise KeyError("All latent entries must include a 'samples' tensor.")
    merged["samples"] = _cat_tensor_sequence(sample_tensors)

    noise_masks = [item.get("noise_mask") for item in flattened if item.get("noise_mask") is not None]
    if noise_masks:
        if len(noise_masks) == len(flattened):
            merged["noise_mask"] = _cat_tensor_sequence(noise_masks)
        else:
            # Skip partial noise masks to avoid batch mismatches.
            pass

    batch_indices = [item.get("batch_index") for item in flattened if item.get("batch_index") is not None]
    if batch_indices:
        merged["batch_index"] = _merge_optional_tensor_sequence(batch_indices)

    # Preserve remaining metadata from the first latent entry, falling back to subsequent entries
    # if the key is missing so that custom metadata survives the merge.
    for item in flattened:
        for key, value in item.items():
            if key in {"samples", "noise_mask", "batch_index"}:
                continue
            if key not in merged:
                merged[key] = deepcopy(value)

    return merged