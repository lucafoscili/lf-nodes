"""Common helpers shared across IPAdapter variants (generic, faceID, etc.).

This file intentionally keeps zero ComfyUI node class logic; only pure helpers.

Design goals:
- Reusable logging (markdown wrapper)
- Vision feature normalization helpers
- Embedding L2 normalization
- Safe extraction of encode fn from a CLIP-Vision like object
"""
import torch

from typing import Any, Callable, Sequence

# region markdown_block
def markdown_block(title: str, lines: Sequence[str]) -> str:
    """
    Generates a Markdown block with a given title and a sequence of lines.

    Args:
        title (str): The title to be used as a Markdown heading.
        lines (Sequence[str]): A sequence of strings, each representing a line to include in the block.

    Returns:
        str: A formatted Markdown string with the title as a level 2 heading followed by the provided lines.
    """
    return f"## {title}\n\n" + "\n".join(lines)
# endregion

# region Vision encoding helpers
def resolve_encode_fn(clip_vision: Any) -> Callable[[torch.Tensor], Any]:
    """
    Resolves and returns the encoding function from a CLIP vision model.

    This function searches for an appropriate image encoding method within the provided
    CLIP vision model object. It checks for the presence of either the 'encode_image' or
    'forward' method, returning the first callable found. If neither method is found,
    a RuntimeError is raised.

    Args:
        clip_vision (Any): The CLIP vision model object to inspect.

    Returns:
        Callable[[torch.Tensor], Any]: The encoding function that processes an image tensor.

    Raises:
        RuntimeError: If no suitable encoding method is found on the model.
    """
    for cand in ("encode_image", "forward"):
        if hasattr(clip_vision, cand):
            fn = getattr(clip_vision, cand)
            if callable(fn):
                return fn
    raise RuntimeError("Unable to locate encode method on clip_vision model.")


def extract_vision_features(encoded: Any) -> tuple[torch.Tensor | None, torch.Tensor | None]:
    """
    Extracts pooled and token-level vision features from an encoded input.

    This function handles both tensor and object-like inputs from a vision encoder.
    - If the input is a tensor:
        - 2D tensor: treated as pooled features.
        - 3D tensor: treated as token-level features.
    - If the input is an object:
        - Tries to extract 'image_embeds' as pooled features.
        - Tries to extract 'last_hidden_state' or the last element of 'hidden_states' as token-level features.

    Args:
        encoded (Any): The encoded output from a vision encoder, which can be a tensor or an object with relevant attributes.

    Returns:
        tuple[torch.Tensor | None, torch.Tensor | None]: 
            A tuple containing:
                - pooled (torch.Tensor or None): The pooled vision features.
                - token_feats (torch.Tensor or None): The token-level vision features.

    Raises:
        ValueError: If the input tensor has an unexpected shape.
    """
    pooled = None
    token_feats = None
    if torch.is_tensor(encoded):
        if encoded.dim() == 2:
            pooled = encoded
        elif encoded.dim() == 3:
            token_feats = encoded
        else:
            raise ValueError(f"Unexpected tensor shape from vision encoder: {tuple(encoded.shape)}")
    else:  # object-like
        if hasattr(encoded, "image_embeds"):
            pooled = getattr(encoded, "image_embeds")
        if hasattr(encoded, "last_hidden_state"):
            token_feats = getattr(encoded, "last_hidden_state")
        elif hasattr(encoded, "hidden_states"):
            hs = getattr(encoded, "hidden_states")
            if isinstance(hs, (list, tuple)) and hs and torch.is_tensor(hs[-1]):
                token_feats = hs[-1]
    return pooled, token_feats


def l2_normalize(t: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """
    Normalizes a tensor using the L2 norm along the last dimension.

    Args:
        t (torch.Tensor): The input tensor to normalize.
        eps (float, optional): A small value added to the norm for numerical stability. Default is 1e-6.

    Returns:
        torch.Tensor: The L2-normalized tensor.

    Raises:
        ValueError: If the input tensor is None.
    """
    if t is None:
        raise ValueError("Cannot normalize None tensor")
    return t / (t.norm(dim=-1, keepdim=True) + eps)


def maybe_unsqueeze_batch(pooled: torch.Tensor) -> torch.Tensor:
    """
    Ensures the input tensor has a batch dimension.

    If the input tensor `pooled` is 1-dimensional, this function adds a batch dimension
    by unsqueezing at position 0. If the tensor already has more than one dimension,
    it is returned unchanged.

    Args:
        pooled (torch.Tensor): The input tensor to be checked and possibly unsqueezed.

    Returns:
        torch.Tensor: The tensor with a batch dimension if it was missing, otherwise the original tensor.
    """
    if pooled.dim() == 1:
        return pooled.unsqueeze(0)
    return pooled
# endregion