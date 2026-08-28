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

def _merge_optional_tensor_sequence(
    values: Iterable[Any],
    batch_sizes: Iterable[int],
) -> Any:
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
    materialized = list(values)
    sizes = list(batch_sizes)
    if len(materialized) != len(sizes):
        raise ValueError("Latent batch_index values must align with latent entries.")

    tensor_flags = [isinstance(value, torch.Tensor) for value in materialized]
    if any(tensor_flags) and not all(tensor_flags):
        raise TypeError(
            "Latent batch_index entries must use one representation: all tensors "
            "or all scalar/sequences."
        )

    if all(tensor_flags):
        expanded_tensors = []
        for value, batch_size in zip(materialized, sizes):
            tensor = value.reshape(1) if value.ndim == 0 else value
            if tensor.shape[0] == 1 and batch_size > 1:
                tensor = tensor.expand(batch_size, *tensor.shape[1:])
            elif tensor.shape[0] != batch_size:
                raise ValueError(
                    "Latent batch_index leading dimension must be 1 or match "
                    f"its samples batch size {batch_size}; got {tensor.shape[0]}."
                )
            expanded_tensors.append(tensor)
        return torch.cat(expanded_tensors, dim=0)

    sequences: List[int] = []
    for value, batch_size in zip(materialized, sizes):
        sequence = list(value) if isinstance(value, (list, tuple)) else [value]
        if len(sequence) == 1 and batch_size > 1:
            sequence = sequence * batch_size
        elif len(sequence) != batch_size:
            raise ValueError(
                "Latent batch_index length must be 1 or match its samples batch "
                f"size {batch_size}; got {len(sequence)}."
            )
        sequences.extend(int(item) for item in sequence)
    return sequences


def _validate_latent_entry(item: Dict[str, Any], index: int) -> None:
    """Validate samples and batch-coupled metadata for one latent entry."""

    if "samples" not in item:
        raise KeyError(f"Latent entry {index} must include a 'samples' tensor.")
    samples = item["samples"]
    if not isinstance(samples, torch.Tensor):
        raise TypeError(f"Latent entry {index} 'samples' must be a torch.Tensor.")
    if samples.ndim != 4 or samples.shape[0] < 1:
        raise ValueError(
            f"Latent entry {index} 'samples' must have shape [B,C,H,W] "
            "with a non-empty batch."
        )

    batch_size = int(samples.shape[0])
    if "noise_mask" in item:
        mask = item["noise_mask"]
        if not isinstance(mask, torch.Tensor):
            raise TypeError("Latent 'noise_mask' must be a torch.Tensor.")
        if mask.ndim == 0:
            raise ValueError("Latent 'noise_mask' must have a batch dimension.")
        if mask.shape[0] not in (1, batch_size):
            raise ValueError(
                "Latent noise_mask leading dimension must be 1 or match its "
                f"samples batch size {batch_size}; got {mask.shape[0]}."
            )

    if "batch_index" in item:
        value = item["batch_index"]
        if isinstance(value, torch.Tensor):
            length = 1 if value.ndim == 0 else int(value.shape[0])
        elif isinstance(value, (list, tuple)):
            length = len(value)
        else:
            length = 1
        if length not in (1, batch_size):
            raise ValueError(
                "Latent batch_index length must be 1 or match its samples batch "
                f"size {batch_size}; got {length}."
            )

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

    for index, item in enumerate(flattened):
        _validate_latent_entry(item, index)

    noise_mask_presence = ["noise_mask" in item for item in flattened]
    if any(noise_mask_presence) and not all(noise_mask_presence):
        raise ValueError(
            "Latent noise_mask must be present on every entry or omitted from "
            "every entry."
        )

    batch_index_presence = ["batch_index" in item for item in flattened]
    if any(batch_index_presence) and not all(batch_index_presence):
        raise ValueError(
            "Latent batch_index must be present on every entry or omitted from "
            "every entry."
        )

    if len(flattened) == 1:
        return {
            key: value if isinstance(value, torch.Tensor) else deepcopy(value)
            for key, value in flattened[0].items()
        }

    merged: Dict[str, Any] = {}

    sample_tensors = [item["samples"] for item in flattened]
    merged["samples"] = _cat_tensor_sequence(sample_tensors)

    noise_masks = [item.get("noise_mask") for item in flattened]
    if all(mask is not None for mask in noise_masks):
        expanded_masks = []
        for item, mask in zip(flattened, noise_masks):
            if not isinstance(mask, torch.Tensor):
                raise TypeError("Latent 'noise_mask' must be a torch.Tensor.")
            batch_size = int(item["samples"].shape[0])
            if mask.ndim == 0:
                raise ValueError("Latent 'noise_mask' must have a batch dimension.")
            if mask.shape[0] == 1 and batch_size > 1:
                mask = mask.expand(batch_size, *mask.shape[1:])
            elif mask.shape[0] != batch_size:
                raise ValueError(
                    "Latent noise_mask leading dimension must be 1 or match its "
                    f"samples batch size {batch_size}; got {mask.shape[0]}."
                )
            expanded_masks.append(mask)
        merged["noise_mask"] = torch.cat(expanded_masks, dim=0)

    batch_indices = [item.get("batch_index") for item in flattened]
    if all(value is not None for value in batch_indices):
        merged["batch_index"] = _merge_optional_tensor_sequence(
            batch_indices,
            [int(item["samples"].shape[0]) for item in flattened],
        )

    # Preserve remaining metadata from the first latent entry, falling back to subsequent entries
    # if the key is missing so that custom metadata survives the merge.
    for item in flattened:
        for key, value in item.items():
            if key in {"samples", "noise_mask", "batch_index"}:
                continue
            if key not in merged:
                merged[key] = (
                    value if isinstance(value, torch.Tensor) else deepcopy(value)
                )

    return merged


def normalize_input_latent_batches(latent_input: Any) -> List[Dict[str, Any]]:
    """Flatten containers while preserving every coherent latent batch.

    Each source dictionary is validated and copied independently.  Unlike
    :func:`normalize_input_latent_list`, this seam never splits its ``samples``
    batch, which preserves temporal or other batch-coupled VAE semantics.
    """

    flattened = _flatten_latent_items(latent_input)
    if not flattened:
        raise ValueError("Latent input is empty. Provide at least one latent sample.")
    return [normalize_input_latent(item) for item in flattened]


def normalize_input_latent_list(latent_input: Any) -> List[Dict[str, Any]]:
    """Flatten latent containers into ordered single-sample latent dictionaries.

    Unlike :func:`normalize_input_latent`, this lossless list seam does not require
    all latent samples to share a spatial shape and therefore does not concatenate
    them. Batch-coupled metadata is sliced by ``normalize_output_latent``.
    """

    flattened = _flatten_latent_items(latent_input)
    if not flattened:
        raise ValueError("Latent input is empty. Provide at least one latent sample.")

    from .normalize_output_latent import normalize_output_latent

    latent_list: List[Dict[str, Any]] = []
    for latent in flattened:
        _, items = normalize_output_latent(latent)
        latent_list.extend(items)
    return latent_list
