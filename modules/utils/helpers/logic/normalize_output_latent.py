import torch

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

    latent_batch = latent_input.copy()

    latent_list = []
    batch_size = samples.shape[0]

    for i in range(batch_size):
        single_sample = samples[i:i+1]  # Shape: [1, C, H, W]
        single_latent = latent_input.copy()
        single_latent["samples"] = single_sample
        latent_list.append(single_latent)

    return latent_batch, latent_list
# endregion