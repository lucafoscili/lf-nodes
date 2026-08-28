import torch
from copy import deepcopy

from typing import Dict, List, Any

# region normalize_output_latent
def normalize_output_latent(latent_input: Dict[str, Any]) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Normalize the given latent input into both batch and list formats.

    This function takes a latent dictionary containing a 'samples' tensor and returns:
    - A batch latent dictionary (same as input, for batch processing)
    - A list of individual latent dictionaries, each with a single sample

    Parameters:
    latent_input (Dict[str, Any]): The latent input dictionary containing at least a 'samples' tensor
        with shape [B, C, H, W] where B is batch size.

    Returns:
    tuple: A tuple containing:
        - latent_batch (Dict[str, Any]): The original latent dictionary for batch processing.
        - latent_list (List[Dict[str, Any]]): A list of latent dictionaries, each containing
          a 'samples' tensor with shape [1, C, H, W].
    """
    if not isinstance(latent_input, dict):
        raise TypeError("Latent input must be a dictionary.")

    if "samples" not in latent_input:
        raise ValueError("Latent input must contain a 'samples' tensor.")

    samples = latent_input["samples"]
    if not isinstance(samples, torch.Tensor):
        raise TypeError("Latent 'samples' must be a torch.Tensor.")

    if len(samples.shape) != 4:
        raise ValueError("Latent 'samples' tensor must be 4D [B, C, H, W].")

    batch_size = samples.shape[0]
    if batch_size < 1:
        raise ValueError("Latent 'samples' batch must contain at least one sample.")

    def copy_metadata(value: Any):
        """Copy mutable metadata without duplicating latent-sized tensors."""
        return value if isinstance(value, torch.Tensor) else deepcopy(value)

    latent_batch = {
        key: copy_metadata(value)
        for key, value in latent_input.items()
    }

    def slice_tensor_metadata(value: torch.Tensor, key: str, index: int):
        if value.ndim == 0:
            return value
        if value.shape[0] == batch_size:
            return value[index : index + 1]
        if value.shape[0] == 1:
            return value
        raise ValueError(
            f"Latent '{key}' leading dimension must be 1 or match samples batch "
            f"size {batch_size}; got {value.shape[0]}."
        )

    def slice_batch_index(value: Any, index: int):
        if isinstance(value, torch.Tensor):
            return slice_tensor_metadata(value, "batch_index", index)
        if isinstance(value, (list, tuple)):
            if len(value) == batch_size:
                selected = [deepcopy(value[index])]
                return tuple(selected) if isinstance(value, tuple) else selected
            if len(value) == 1:
                return deepcopy(value)
            raise ValueError(
                "Latent 'batch_index' length must be 1 or match samples batch "
                f"size {batch_size}; got {len(value)}."
            )
        return deepcopy(value)

    latent_list = []

    for i in range(batch_size):
        single_sample = samples[i:i+1]  # Shape: [1, C, H, W]
        single_latent = {}
        for key, value in latent_input.items():
            if key == "samples":
                single_latent[key] = single_sample
            elif key == "noise_mask":
                if not isinstance(value, torch.Tensor):
                    raise TypeError("Latent 'noise_mask' must be a torch.Tensor.")
                single_latent[key] = slice_tensor_metadata(value, key, i)
            elif key == "batch_index":
                single_latent[key] = slice_batch_index(value, i)
            else:
                single_latent[key] = copy_metadata(value)
        latent_list.append(single_latent)

    return latent_batch, latent_list
# endregion


def normalize_output_latents(
    latent_inputs: Any,
) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Return a compatible primary latent batch plus a lossless ordered list.

    Multiple spatial shapes cannot share one LATENT batch. Inputs are therefore
    split without copying tensor storage, grouped by sample compatibility, and
    only the first compatible group is concatenated for the legacy batch socket.
    The list output retains every sample in source order.
    """

    def flatten(value: Any) -> List[Dict[str, Any]]:
        if isinstance(value, dict):
            return [value]
        if isinstance(value, (list, tuple)):
            flattened: List[Dict[str, Any]] = []
            for item in value:
                flattened.extend(flatten(item))
            return flattened
        raise TypeError(
            "Latent output must be a dictionary or a nested list of dictionaries."
        )

    source_latents = flatten(latent_inputs)
    if not source_latents:
        raise ValueError("Latent output is empty. Provide at least one latent sample.")

    latent_list: List[Dict[str, Any]] = []
    for latent in source_latents:
        _, items = normalize_output_latent(latent)
        latent_list.extend(items)

    first_samples = latent_list[0]["samples"]
    signature = (
        tuple(first_samples.shape[1:]),
        first_samples.dtype,
        first_samples.device,
    )
    first_group = [
        latent
        for latent in latent_list
        if (
            tuple(latent["samples"].shape[1:]),
            latent["samples"].dtype,
            latent["samples"].device,
        ) == signature
    ]

    from .normalize_input_latent import normalize_input_latent

    return normalize_input_latent(first_group), latent_list
