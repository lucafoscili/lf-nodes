import torch
from copy import deepcopy
from typing import Any, Dict, Iterable, List

def _flatten_latent_items(latent_input: Any) -> List[Dict[str, Any]]:
    """
    Flattens a nested structure of latent inputs into a list of dictionaries.

    Args:
        latent_input (Any): The input to be flattened. Can be a dictionary, a list/tuple of dictionaries, or nested lists/tuples containing dictionaries.

    Returns:
        List[Dict[str, Any]]: A flat list of dictionaries extracted from the input.

    Raises:
        TypeError: If the input is not a dictionary, list, or tuple containing dictionaries.
    """
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
    """
    Concatenates a sequence of torch.Tensor objects along the first dimension.

    Skips any None values in the input sequence. If a tensor is zero-dimensional,
    it is unsqueezed to become one-dimensional before concatenation. Raises a
    TypeError if any non-tensor value is encountered, and a ValueError if no
    valid tensors are found to concatenate.

    Args:
        values (Iterable[torch.Tensor]): An iterable of torch.Tensor objects, possibly containing None.

    Returns:
        torch.Tensor: A single tensor resulting from concatenation along the first dimension.

    Raises:
        TypeError: If any non-tensor value is encountered in the input sequence.
        ValueError: If no valid tensors are found to concatenate.
    """
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
    """
    Merges a sequence of optional tensor or integer values.
    If any of the values are PyTorch tensors, concatenates them using `_cat_tensor_sequence`.
    Otherwise, collects all integer values from the sequence, flattening any nested lists or tuples.
    Ignores `None` values.
    Args:
        values (Iterable[Any]): An iterable containing tensors, integers, lists/tuples of integers, or None.
    Returns:
        Any: Concatenated tensor if any tensors are present; otherwise, a list of integers (flattened), or None if no values remain.
    """
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
    Normalizes and merges one or more latent input dictionaries into a single standardized latent dictionary.
    This function flattens the input, validates the presence of required tensors, and merges multiple latent samples
    into a single batch. It concatenates 'samples' tensors, optionally merges 'noise_mask' and 'batch_index' if present,
    and preserves additional metadata from the first entry (falling back to subsequent entries if missing).

    Args:
        latent_input (Any): A latent input or sequence of latent inputs, each expected to be a dictionary
            containing at least a 'samples' tensor and optional 'noise_mask', 'batch_index', and other metadata.

    Returns:
        Dict[str, Any]: A normalized latent dictionary containing merged tensors and preserved metadata.
        
    Raises:
        ValueError: If the input is empty.
        KeyError: If any latent entry is missing the required 'samples' tensor.
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