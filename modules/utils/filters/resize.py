import torch

from ...utils.helpers.conversion import convert_to_int
from ...utils.helpers.torch import resize_and_crop_image, resize_image
from ...utils.constants import RESIZE_MODE_COMBO

# region Helpers
def _normalize_resampler(raw: str | None) -> str:
    """
    Map an arbitrary resampler string to one of the known interpolation modes.
    The UI exposes \"Lanczos\" and \"Linear\" for familiarity, but our tensor
    backend only supports a subset of modes. We therefore map:

      - \"lanczos\"  -> \"bicubic\"  (high‑quality tensor fallback)
      - \"linear\"   -> \"bilinear\"
      - \"nearest exact\" -> \"nearest exact\"

    and default to \"bicubic\" when the value is missing or unknown.
    """
    candidate = str(raw).strip().lower() if raw else ""

    # Map UI-only / unsupported tensor modes to safe equivalents
    if candidate in ("", "lanczos"):
        return "bicubic"
    if candidate == "linear":
        return "bilinear"

    if candidate in ("nearest", "nearest exact", "bilinear", "bicubic"):
        return candidate

    return "bicubic"
# endregion

# region resize_edge_effect
def resize_edge_effect(image: torch.Tensor, settings: dict) -> torch.Tensor:
    """
    Resize the image based on one edge while preserving aspect ratio.

    Settings:
      - \"longest_edge\" (bool): if True, fit the longest edge; otherwise the shortest.
      - \"size_px\" (int/float/str): target size in pixels for the chosen edge.
      - \"resize_method\" (str): interpolation method (e.g. bicubic, bilinear, lanczos).
    """
    longest_raw = settings.get("longest_edge", True)
    longest_edge = bool(longest_raw)

    size_raw = settings.get("size_px")
    size_val = convert_to_int(size_raw) if size_raw is not None else None
    if size_val is None or int(size_val) <= 0:
        # No-op: invalid or zero size.
        return image

    size_px = int(size_val)
    method = _normalize_resampler(settings.get("resize_method"))

    return resize_image(image, method, longest_edge, size_px)
# endregion

# region resize_free_effect
def resize_free_effect(image: torch.Tensor, settings: dict) -> torch.Tensor:
    """
    Resize the image to explicit width/height with optional crop/pad.

    Settings:
      - \"height\" (int): target height in pixels.
      - \"width\" (int): target width in pixels.
      - \"resize_method\" (str): interpolation method.
      - \"resize_mode\" (str): \"crop\" or \"pad\" (defaults to \"crop\").
      - \"pad_color\" (str): hex color for padding when resize_mode==\"pad\".
    """
    h_raw = settings.get("height")
    w_raw = settings.get("width")

    h_val = convert_to_int(h_raw) if h_raw is not None else None
    w_val = convert_to_int(w_raw) if w_raw is not None else None
    if h_val is None or w_val is None or int(h_val) <= 0 or int(w_val) <= 0:
        return image

    target_h = int(h_val)
    target_w = int(w_val)

    method = _normalize_resampler(settings.get("resize_method"))

    mode_raw = (settings.get("resize_mode") or "crop").strip().lower()
    resize_mode = mode_raw if mode_raw in RESIZE_MODE_COMBO else "crop"

    pad_color_raw = settings.get("pad_color") or "000000"
    pad_color = str(pad_color_raw).lstrip("#")

    return resize_and_crop_image(image, method, target_h, target_w, resize_mode, pad_color)
# endregion
