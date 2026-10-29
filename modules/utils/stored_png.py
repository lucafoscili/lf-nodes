"""PNG files as their stored values, for nodes that must give back exactly what they read.

Core's image load and save are 8-bit RGB, turn alpha into an inverted mask and
truncate on save, so a value that goes in and comes back out can land one level
low. These helpers keep the file's own values instead:

- ``read_png(data)``: the stored pixels as ``uint8`` or ``uint16`` ``[H, W, C]``
  in RGB(A) order, grey kept as one channel, alpha a plain channel. No colour
  management, gamma or orientation is applied; palette images are expanded to
  their colours, and 1, 2 and 4-bit grey is scaled to 8 bits, as PNG defines.
- ``to_tensor(pixels)``: ``[1, H, W, C]`` float32 in 0..1 (value / 255 or
  value / 65535), grey widened to RGB and grey with alpha to RGBA so every
  image node can consume it.
- ``from_tensor(image, bit_depth)``: back to stored values, rounded to the
  nearest level (never truncated). Every 8 or 16-bit value read by
  ``to_tensor`` comes back unchanged.
- ``write_png(pixels, compress_level)``: PNG bytes holding only the pixels: no
  text, time or colour chunks.

OpenCV does the coding: Pillow cannot write 16-bit colour PNG.
"""
from __future__ import annotations

import hashlib
import struct

import numpy as np
import torch

BIT_DEPTHS = (8, 16)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_TYPES = {0: "grey", 2: "rgb", 3: "palette", 4: "grey_alpha", 6: "rgba"}
ROUNDING = "nearest"


def _cv2():
    import cv2  # Lazy: OpenCV is a declared dependency, but only these nodes need it here.

    return cv2


def png_header(data: bytes) -> dict:
    """The IHDR facts of a PNG: width, height, bit depth and colour type."""
    if not isinstance(data, (bytes, bytearray, memoryview)) or bytes(data[:8]) != PNG_SIGNATURE:
        raise ValueError("Not a PNG file: the PNG signature is missing.")
    if len(data) < 33 or bytes(data[12:16]) != b"IHDR":
        raise ValueError("Malformed PNG: the IHDR chunk is missing.")
    width, height, bit_depth, color_type = struct.unpack(">IIBB", bytes(data[16:26]))
    if color_type not in COLOR_TYPES:
        raise ValueError(f"Malformed PNG: colour type {color_type} is not defined.")
    return {"width": width, "height": height, "bit_depth": bit_depth, "color_type": COLOR_TYPES[color_type]}


def read_png(data: bytes) -> tuple[np.ndarray, dict]:
    """Decode PNG bytes to stored values ``[H, W, C]`` (RGB order) and the file's header facts."""
    header = png_header(data)
    cv2 = _cv2()
    pixels = cv2.imdecode(np.frombuffer(bytes(data), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if pixels is None:
        raise ValueError("Malformed PNG: OpenCV could not decode it.")
    if pixels.dtype not in (np.uint8, np.uint16):
        raise ValueError(f"PNG decoded to {pixels.dtype} values; only 8 and 16-bit are read.")
    if pixels.ndim == 2:
        pixels = pixels[..., None]
    channels = pixels.shape[2]
    if channels == 3:
        pixels = pixels[..., ::-1]
    elif channels == 4:
        pixels = pixels[..., [2, 1, 0, 3]]
    elif channels != 1:
        raise ValueError(f"PNG decoded to {channels} channels; expected 1, 3 or 4.")
    if header["color_type"] == "grey_alpha" and channels == 4:
        pixels = pixels[..., [0, 3]]  # OpenCV widens grey+alpha to BGRA; keep what the file stores.
    if pixels.shape[:2] != (header["height"], header["width"]):
        raise ValueError("Malformed PNG: decoded size differs from its header.")
    return np.ascontiguousarray(pixels), header


def to_tensor(pixels: np.ndarray) -> torch.Tensor:
    """Stored values to a ``[1, H, W, C]`` float32 image in 0..1; grey becomes RGB, grey+alpha RGBA."""
    pixels = np.asarray(pixels)
    if pixels.dtype == np.uint8:
        scale = 255.0
    elif pixels.dtype == np.uint16:
        scale = 65535.0
    else:
        raise ValueError(f"Stored values must be uint8 or uint16, not {pixels.dtype}.")
    if pixels.ndim != 3 or pixels.shape[2] not in (1, 2, 3, 4):
        raise ValueError(f"Stored values must be [H, W, 1..4], not {list(pixels.shape)}.")
    if pixels.shape[2] == 1:
        pixels = np.repeat(pixels, 3, axis=2)
    elif pixels.shape[2] == 2:
        pixels = np.concatenate([np.repeat(pixels[..., :1], 3, axis=2), pixels[..., 1:]], axis=2)
    # float32 division of an integer level is correctly rounded, and ``round(x * scale)`` in float32 gives every
    # 8 and 16-bit level back exactly (checked over all 65,536 values).
    return torch.from_numpy(np.ascontiguousarray(pixels)).to(torch.float32).div_(scale)[None]


def from_tensor(image: torch.Tensor, bit_depth: int) -> np.ndarray:
    """A ``[H, W, C]`` (C 1, 3 or 4) image in 0..1 to stored values, rounded to the nearest level."""
    if bit_depth not in BIT_DEPTHS:
        raise ValueError(f"bit_depth must be 8 or 16, not {bit_depth!r}.")
    if not isinstance(image, torch.Tensor):
        raise TypeError("Expected an image tensor.")
    if image.ndim == 4 and image.shape[0] == 1:
        image = image[0]
    if image.ndim != 3 or image.shape[2] not in (1, 3, 4):
        raise ValueError(f"Expected one [H, W, C] image with 1, 3 or 4 channels, not {list(image.shape)}.")
    values = image.detach().to(device="cpu", dtype=torch.float32)
    if not bool(torch.isfinite(values).all()):
        raise ValueError("The image holds NaN or infinite values; they have no stored level.")
    top = 255 if bit_depth == 8 else 65535
    levels = values.clamp(0.0, 1.0).mul_(top).round_()  # half to even, as numpy's rint
    return np.ascontiguousarray(levels.numpy().astype(np.uint8 if bit_depth == 8 else np.uint16))


def write_png(pixels: np.ndarray, compress_level: int = 4) -> bytes:
    """PNG bytes for stored values ``[H, W, C]`` (C 1, 2, 3 or 4; uint8 or uint16), pixels only."""
    if not isinstance(compress_level, int) or isinstance(compress_level, bool) or not 0 <= compress_level <= 9:
        raise ValueError(f"compress_level must be an integer from 0 to 9, not {compress_level!r}.")
    pixels = np.asarray(pixels)
    if pixels.dtype not in (np.uint8, np.uint16) or pixels.ndim != 3 or pixels.shape[2] not in (1, 2, 3, 4):
        raise ValueError(f"Cannot write {pixels.dtype} values of shape {list(pixels.shape)} as PNG.")
    channels = pixels.shape[2]
    if channels == 2:
        # OpenCV writes no grey+alpha PNG; RGBA keeps every value.
        pixels = np.concatenate([np.repeat(pixels[..., :1], 3, axis=2), pixels[..., 1:]], axis=2)
        channels = 4
    if channels == 1:
        ordered = pixels[..., 0]
    elif channels == 3:
        ordered = pixels[..., ::-1]
    else:
        ordered = pixels[..., [2, 1, 0, 3]]
    cv2 = _cv2()
    ok, encoded = cv2.imencode(".png", np.ascontiguousarray(ordered), [cv2.IMWRITE_PNG_COMPRESSION, compress_level])
    if not ok:
        raise ValueError("OpenCV could not encode the PNG.")
    return encoded.tobytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
