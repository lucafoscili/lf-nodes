from __future__ import annotations

import hashlib
import io
import json
import os
import struct
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import PIL
import torch
from PIL import Image

from ...dds_formats import MIP_POLICIES, PIXEL_FORMATS


DDS_ERROR_SCHEMA = "lf.dds.error.v1"
DDS_RECEIPT_SCHEMA = "lf.dds.receipt.v1"
DDS_WRITER_NAME = "lf.dds.writer"
DDS_WRITER_REVISION = "1"
PINNED_PILLOW_REVISION = "12.2.0"

_DDS_MAGIC = b"DDS "
_DDS_HEADER_BYTES = 128

_DDSD_CAPS = 0x00000001
_DDSD_HEIGHT = 0x00000002
_DDSD_WIDTH = 0x00000004
_DDSD_PITCH = 0x00000008
_DDSD_PIXELFORMAT = 0x00001000
_DDSD_MIPMAPCOUNT = 0x00020000
_DDSD_LINEARSIZE = 0x00080000

_DDPF_ALPHAPIXELS = 0x00000001
_DDPF_FOURCC = 0x00000004
_DDPF_RGB = 0x00000040

_DDSCAPS_COMPLEX = 0x00000008
_DDSCAPS_TEXTURE = 0x00001000
_DDSCAPS_MIPMAP = 0x00400000

_FOURCC_DXT1 = struct.unpack("<I", b"DXT1")[0]
_FOURCC_DXT5 = struct.unpack("<I", b"DXT5")[0]


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


class DDSOutputError(ValueError):
    """Fail-closed DDS error with a stable, machine-readable string payload."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.payload = {
            "schema": DDS_ERROR_SCHEMA,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        }
        super().__init__(_canonical_json(self.payload))


class DDSFileCustody:
    """Private hard-link proof retained until a node batch commits or rolls back."""

    __slots__ = ("target", "guard")

    def __init__(self, target: Path, guard: Path) -> None:
        self.target = target
        self.guard = guard

    def commit(self) -> None:
        """Release the private proof after the complete batch succeeds."""

        try:
            self.guard.unlink(missing_ok=True)
        except OSError:
            # The final file is already complete and verified. A guard cleanup
            # failure must not turn a valid output into an ambiguous execution.
            pass

    def rollback(self) -> None:
        """Remove the target only while it is still the guarded LF-owned file."""

        try:
            if not self.target.is_symlink() and os.path.samefile(
                self.guard,
                self.target,
            ):
                self.target.unlink(missing_ok=True)
        except OSError:
            # Cleanup is best effort and must preserve the original stable error.
            pass
        finally:
            try:
                self.guard.unlink(missing_ok=True)
            except OSError:
                pass


def _error(
    code: str,
    message: str,
    **details: Any,
) -> DDSOutputError:
    return DDSOutputError(code, message, details)


def _require_backend() -> None:
    if PIL.__version__ != PINNED_PILLOW_REVISION:
        raise _error(
            "unsupported_backend",
            "The deterministic DDS codec backend revision is unavailable.",
            backend="Pillow",
            expected_revision=PINNED_PILLOW_REVISION,
            actual_revision=PIL.__version__,
        )


def normalize_tensor_image(image: torch.Tensor) -> np.ndarray:
    """Normalize one Comfy IMAGE tensor to deterministic RGB/RGBA uint8 pixels.

    Floating-point inputs are clamped to [0, 1] and quantized with round-half-up.
    Alpha is retained; format-specific policy is applied only after normalization.
    """

    if not isinstance(image, torch.Tensor):
        raise _error(
            "invalid_dimensions",
            "DDS input must be a torch IMAGE tensor.",
            value_type=type(image).__name__,
        )

    tensor = image.detach()
    if tensor.ndim == 4:
        if tensor.shape[0] != 1:
            raise _error(
                "invalid_dimensions",
                "Each normalized DDS image must have a batch size of one.",
                shape=list(tensor.shape),
            )
        tensor = tensor[0]
    if tensor.ndim != 3:
        raise _error(
            "invalid_dimensions",
            "DDS images must have shape [H, W, C].",
            shape=list(tensor.shape),
        )

    height, width, channels = (int(value) for value in tensor.shape)
    if height < 1 or width < 1 or channels not in (3, 4):
        raise _error(
            "invalid_dimensions",
            "DDS images require positive dimensions and three or four channels.",
            width=width,
            height=height,
            channels=channels,
        )

    if tensor.is_floating_point():
        values = tensor.to(device="cpu", dtype=torch.float32).numpy().astype(np.float64)
        if not np.isfinite(values).all():
            raise _error(
                "encode_failure",
                "DDS input contains non-finite pixel values.",
            )
        values = np.clip(values, 0.0, 1.0)
        return np.floor(values * 255.0 + 0.5).astype(np.uint8)

    if tensor.dtype == torch.uint8:
        return tensor.to(device="cpu").numpy().copy()

    raise _error(
        "encode_failure",
        "DDS input uses an unsupported tensor dtype.",
        dtype=str(tensor.dtype),
    )


def _prepare_pixels(
    pixels: np.ndarray,
    pixel_format: str,
) -> tuple[np.ndarray, str]:
    if pixel_format not in PIXEL_FORMATS:
        raise _error(
            "unsupported_format",
            "The requested DDS pixel format is unsupported.",
            pixel_format=pixel_format,
            supported=list(PIXEL_FORMATS),
        )
    if not isinstance(pixels, np.ndarray) or pixels.dtype != np.uint8 or pixels.ndim != 3:
        raise _error(
            "invalid_dimensions",
            "Normalized DDS pixels must be an HWC uint8 array.",
        )

    channels = int(pixels.shape[2])
    if channels not in (3, 4) or pixels.shape[0] < 1 or pixels.shape[1] < 1:
        raise _error(
            "invalid_dimensions",
            "Normalized DDS pixels require positive dimensions and RGB or RGBA channels.",
            shape=list(pixels.shape),
        )

    wants_alpha = pixel_format in ("RGBA32", "BC3")
    has_alpha = channels == 4

    if not wants_alpha:
        if has_alpha:
            alpha = pixels[..., 3]
            non_opaque = int(np.count_nonzero(alpha != 255))
            if non_opaque:
                raise _error(
                    "invalid_alpha",
                    "The requested DDS format cannot discard non-opaque alpha.",
                    pixel_format=pixel_format,
                    non_opaque_pixels=non_opaque,
                    minimum_alpha=int(alpha.min()),
                )
            return pixels[..., :3].copy(), "opaque_required"
        return pixels.copy(), "none"

    if has_alpha:
        return pixels.copy(), "preserve"

    alpha = np.full((*pixels.shape[:2], 1), 255, dtype=np.uint8)
    return np.concatenate((pixels, alpha), axis=2), "opaque_fill"


def _generate_levels(pixels: np.ndarray, mip_policy: str) -> list[np.ndarray]:
    if mip_policy not in MIP_POLICIES:
        raise _error(
            "unsupported_format",
            "The requested DDS mip policy is unsupported.",
            mip_policy=mip_policy,
            supported=list(MIP_POLICIES),
        )

    levels = [pixels]
    if mip_policy == "none":
        return levels

    _require_backend()
    while levels[-1].shape[0] > 1 or levels[-1].shape[1] > 1:
        previous = levels[-1]
        next_width = max(1, int(previous.shape[1]) // 2)
        next_height = max(1, int(previous.shape[0]) // 2)
        try:
            image = Image.fromarray(previous)
            resized = image.resize(
                (next_width, next_height),
                Image.Resampling.LANCZOS,
                reducing_gap=None,
            )
            levels.append(np.asarray(resized, dtype=np.uint8).copy())
        except Exception as error:
            raise _error(
                "encode_failure",
                "DDS mip generation failed.",
                backend="Pillow",
                backend_revision=PIL.__version__,
            ) from error
    return levels


def _compressed_level_size(width: int, height: int, pixel_format: str) -> int:
    block_bytes = 8 if pixel_format == "BC1" else 16
    return max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block_bytes


def _encode_bcn_level(level: np.ndarray, pixel_format: str) -> bytes:
    _require_backend()
    pillow_format = "DXT1" if pixel_format == "BC1" else "DXT5"
    expected_fourcc = _FOURCC_DXT1 if pixel_format == "BC1" else _FOURCC_DXT5
    try:
        image = Image.fromarray(level)
        output = io.BytesIO()
        image.save(output, format="DDS", pixel_format=pillow_format)
        encoded = output.getvalue()
    except Exception as error:
        raise _error(
            "encode_failure",
            "DDS block compression failed.",
            pixel_format=pixel_format,
            backend="Pillow",
            backend_revision=PIL.__version__,
        ) from error

    if len(encoded) < _DDS_HEADER_BYTES or encoded[:4] != _DDS_MAGIC:
        raise _error(
            "encode_failure",
            "DDS block compressor returned an invalid payload.",
            pixel_format=pixel_format,
        )
    header = struct.unpack("<31I", encoded[4:_DDS_HEADER_BYTES])
    if header[20] != expected_fourcc:
        raise _error(
            "encode_failure",
            "DDS block compressor returned the wrong legacy format.",
            pixel_format=pixel_format,
        )

    payload = encoded[_DDS_HEADER_BYTES:]
    expected_size = _compressed_level_size(level.shape[1], level.shape[0], pixel_format)
    if len(payload) != expected_size:
        raise _error(
            "encode_failure",
            "DDS block compressor returned an unexpected byte length.",
            pixel_format=pixel_format,
            expected_byte_length=expected_size,
            actual_byte_length=len(payload),
        )
    return payload


def _encode_raw_level(level: np.ndarray, pixel_format: str) -> bytes:
    if pixel_format == "RGB24":
        return level[..., [2, 1, 0]].tobytes(order="C")
    return level[..., [2, 1, 0, 3]].tobytes(order="C")


def _build_header(
    width: int,
    height: int,
    pixel_format: str,
    mip_count: int,
) -> bytes:
    compressed = pixel_format in ("BC1", "BC3")
    flags = _DDSD_CAPS | _DDSD_HEIGHT | _DDSD_WIDTH | _DDSD_PIXELFORMAT
    if compressed:
        flags |= _DDSD_LINEARSIZE
        pitch_or_linear_size = _compressed_level_size(width, height, pixel_format)
        pixel_flags = _DDPF_FOURCC
        fourcc = _FOURCC_DXT1 if pixel_format == "BC1" else _FOURCC_DXT5
        bit_count = 0
        masks = (0, 0, 0, 0)
    else:
        flags |= _DDSD_PITCH
        bytes_per_pixel = 3 if pixel_format == "RGB24" else 4
        pitch_or_linear_size = width * bytes_per_pixel
        pixel_flags = _DDPF_RGB
        if pixel_format == "RGBA32":
            pixel_flags |= _DDPF_ALPHAPIXELS
        fourcc = 0
        bit_count = bytes_per_pixel * 8
        masks = (
            0x00FF0000,
            0x0000FF00,
            0x000000FF,
            0xFF000000 if pixel_format == "RGBA32" else 0,
        )

    caps = _DDSCAPS_TEXTURE
    header_mip_count = 0
    if mip_count > 1:
        flags |= _DDSD_MIPMAPCOUNT
        caps |= _DDSCAPS_COMPLEX | _DDSCAPS_MIPMAP
        header_mip_count = mip_count

    values = (
        124,
        flags,
        height,
        width,
        pitch_or_linear_size,
        0,
        header_mip_count,
        *((0,) * 11),
        32,
        pixel_flags,
        fourcc,
        bit_count,
        *masks,
        caps,
        0,
        0,
        0,
        0,
    )
    return _DDS_MAGIC + struct.pack("<31I", *values)


def read_dds_header(data: bytes) -> dict[str, Any]:
    """Read and strictly validate the LF DDS v1 legacy header and payload size."""

    if not isinstance(data, bytes) or len(data) < _DDS_HEADER_BYTES:
        raise _error(
            "readback_mismatch",
            "DDS readback is shorter than the legacy header.",
            byte_length=len(data) if isinstance(data, bytes) else None,
        )
    if data[:4] != _DDS_MAGIC:
        raise _error(
            "readback_mismatch",
            "DDS readback has the wrong magic bytes.",
        )

    values = struct.unpack("<31I", data[4:_DDS_HEADER_BYTES])
    (
        header_size,
        flags,
        height,
        width,
        pitch_or_linear_size,
        _depth,
        header_mip_count,
    ) = values[:7]
    pixel_format_size = values[18]
    pixel_flags = values[19]
    fourcc = values[20]
    bit_count = values[21]
    masks = tuple(values[22:26])
    caps = values[26]
    trailing_caps = tuple(values[27:31])
    reserved = tuple(values[7:18])

    if header_size != 124 or pixel_format_size != 32 or width < 1 or height < 1:
        raise _error(
            "readback_mismatch",
            "DDS readback contains invalid dimensions or header sizes.",
            width=width,
            height=height,
            header_size=header_size,
            pixel_format_size=pixel_format_size,
        )

    if _depth != 0 or any(reserved) or any(trailing_caps):
        raise _error(
            "readback_mismatch",
            "DDS readback contains unsupported legacy header fields.",
        )

    if pixel_flags == _DDPF_FOURCC:
        if fourcc == _FOURCC_DXT1:
            pixel_format = "BC1"
            alpha_semantics = "none"
        elif fourcc == _FOURCC_DXT5:
            pixel_format = "BC3"
            alpha_semantics = "straight"
        else:
            raise _error(
                "readback_mismatch",
                "DDS readback contains an unsupported FOURCC.",
                fourcc=struct.pack("<I", fourcc).decode("latin-1"),
            )
        if bit_count != 0 or any(masks):
            raise _error(
                "readback_mismatch",
                "DDS compressed pixel format fields are inconsistent.",
                bit_count=bit_count,
                masks=list(masks),
            )
        expected_top_size = _compressed_level_size(width, height, pixel_format)
        if not flags & _DDSD_LINEARSIZE or pitch_or_linear_size != expected_top_size:
            raise _error(
                "readback_mismatch",
                "DDS compressed linear size does not match the payload.",
                expected=expected_top_size,
                actual=pitch_or_linear_size,
            )
    else:
        rgb24_masks = (0x00FF0000, 0x0000FF00, 0x000000FF, 0)
        rgba32_masks = (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
        if (
            pixel_flags == _DDPF_RGB
            and fourcc == 0
            and bit_count == 24
            and masks == rgb24_masks
        ):
            pixel_format = "RGB24"
            alpha_semantics = "none"
            bytes_per_pixel = 3
        elif (
            pixel_flags == (_DDPF_RGB | _DDPF_ALPHAPIXELS)
            and fourcc == 0
            and bit_count == 32
            and masks == rgba32_masks
        ):
            pixel_format = "RGBA32"
            alpha_semantics = "straight"
            bytes_per_pixel = 4
        else:
            raise _error(
                "readback_mismatch",
                "DDS readback contains unsupported uncompressed masks.",
                bit_count=bit_count,
                pixel_flags=pixel_flags,
                masks=list(masks),
            )
        expected_top_size = width * bytes_per_pixel
        if not flags & _DDSD_PITCH or pitch_or_linear_size != expected_top_size:
            raise _error(
                "readback_mismatch",
                "DDS uncompressed pitch does not match the payload.",
                expected=expected_top_size,
                actual=pitch_or_linear_size,
            )

    if header_mip_count == 1:
        raise _error(
            "readback_mismatch",
            "DDS single-level files must omit the mip-count field.",
        )
    mip_count = header_mip_count or 1
    expected_flags = _DDSD_CAPS | _DDSD_HEIGHT | _DDSD_WIDTH | _DDSD_PIXELFORMAT
    expected_flags |= _DDSD_LINEARSIZE if pixel_format in ("BC1", "BC3") else _DDSD_PITCH
    expected_caps = _DDSCAPS_TEXTURE
    if mip_count > 1:
        expected_flags |= _DDSD_MIPMAPCOUNT
        expected_caps |= _DDSCAPS_COMPLEX | _DDSCAPS_MIPMAP
    if flags != expected_flags or caps != expected_caps:
        raise _error(
            "readback_mismatch",
            "DDS flags and capability fields disagree with its payload contract.",
            mip_count=mip_count,
            expected_flags=expected_flags,
            actual_flags=flags,
            expected_caps=expected_caps,
            actual_caps=caps,
        )

    expected_payload_size = 0
    level_width = width
    level_height = height
    for level_index in range(mip_count):
        if pixel_format in ("BC1", "BC3"):
            expected_payload_size += _compressed_level_size(
                level_width,
                level_height,
                pixel_format,
            )
        else:
            bytes_per_pixel = 3 if pixel_format == "RGB24" else 4
            expected_payload_size += level_width * level_height * bytes_per_pixel
        if level_index < mip_count - 1:
            if level_width == 1 and level_height == 1:
                raise _error(
                    "readback_mismatch",
                    "DDS readback contains too many mip levels.",
                    mip_count=mip_count,
                )
            level_width = max(1, level_width // 2)
            level_height = max(1, level_height // 2)

    expected_byte_length = _DDS_HEADER_BYTES + expected_payload_size
    if len(data) != expected_byte_length:
        raise _error(
            "readback_mismatch",
            "DDS readback byte length does not match its header.",
            expected_byte_length=expected_byte_length,
            actual_byte_length=len(data),
        )

    return {
        "width": width,
        "height": height,
        "pixel_format": pixel_format,
        "alpha_semantics": alpha_semantics,
        "mip_count": mip_count,
        "pitch_or_linear_size": pitch_or_linear_size,
        "byte_length": len(data),
    }


def _verify_dds_bytes(
    data: bytes,
    *,
    width: int,
    height: int,
    pixel_format: str,
    mip_count: int,
) -> dict[str, Any]:
    header = read_dds_header(data)
    expected = {
        "width": width,
        "height": height,
        "pixel_format": pixel_format,
        "alpha_semantics": "none" if pixel_format in ("RGB24", "BC1") else "straight",
        "mip_count": mip_count,
    }
    mismatches = {
        key: {"expected": value, "actual": header.get(key)}
        for key, value in expected.items()
        if header.get(key) != value
    }
    if mismatches:
        raise _error(
            "readback_mismatch",
            "DDS readback does not match the requested output contract.",
            mismatches=mismatches,
        )
    return header


def encode_dds(
    pixels: np.ndarray,
    pixel_format: str,
    mip_policy: str,
) -> tuple[bytes, dict[str, Any]]:
    prepared, alpha_policy = _prepare_pixels(pixels, pixel_format)
    levels = _generate_levels(prepared, mip_policy)

    try:
        if pixel_format in ("BC1", "BC3"):
            payload = b"".join(_encode_bcn_level(level, pixel_format) for level in levels)
            backend = {
                "name": "Pillow BCN",
                "revision": PINNED_PILLOW_REVISION,
            }
        else:
            payload = b"".join(_encode_raw_level(level, pixel_format) for level in levels)
            backend = (
                {
                    "name": "Pillow resampler",
                    "revision": PINNED_PILLOW_REVISION,
                }
                if len(levels) > 1
                else {"name": "LF raw", "revision": DDS_WRITER_REVISION}
            )
        header = _build_header(
            width=int(prepared.shape[1]),
            height=int(prepared.shape[0]),
            pixel_format=pixel_format,
            mip_count=len(levels),
        )
        data = header + payload
        parsed = _verify_dds_bytes(
            data,
            width=int(prepared.shape[1]),
            height=int(prepared.shape[0]),
            pixel_format=pixel_format,
            mip_count=len(levels),
        )
    except DDSOutputError:
        raise
    except Exception as error:
        raise _error(
            "encode_failure",
            "DDS encoding failed.",
            pixel_format=pixel_format,
        ) from error

    receipt = {
        "width": parsed["width"],
        "height": parsed["height"],
        "pixel_format": pixel_format,
        "alpha_policy": alpha_policy,
        "mip_policy": mip_policy,
        "mip_count": parsed["mip_count"],
        "byte_length": len(data),
        "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
        "encoder": {
            "name": DDS_WRITER_NAME,
            "revision": DDS_WRITER_REVISION,
            "backend": backend,
        },
        "normalization": {
            "range": "clamp_0_1",
            "quantization": "round_half_up_u8",
            "mip_filter": "none" if mip_policy == "none" else "pillow_lanczos",
            "colorspace": "srgb_encoded",
            "alpha_filter": (
                "none"
                if mip_policy == "none" or pixel_format in ("RGB24", "BC1")
                else "premultiplied"
            ),
            "dimension_rule": "floor_half_until_1x1",
        },
    }
    return data, receipt


def write_dds_atomic(
    output_file: str | Path,
    data: bytes,
    expected: dict[str, Any],
    *,
    retain_custody: bool = False,
) -> DDSFileCustody | None:
    """Publish one complete DDS file atomically without replacing an existing path."""

    target = Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=target.parent,
    )
    temporary = Path(temporary_name)
    published = False
    custody: DDSFileCustody | None = None
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

        staged = temporary.read_bytes()
        _verify_dds_bytes(
            staged,
            width=int(expected["width"]),
            height=int(expected["height"]),
            pixel_format=str(expected["pixel_format"]),
            mip_count=int(expected["mip_count"]),
        )
        if "sha256:" + hashlib.sha256(staged).hexdigest() != expected["sha256"]:
            raise _error(
                "readback_mismatch",
                "Staged DDS checksum does not match the encoder receipt.",
            )

        try:
            os.link(temporary, target)
        except FileExistsError as error:
            raise _error(
                "encode_failure",
                "DDS publication target became occupied before publication.",
                stage="publish_no_clobber",
            ) from error
        except OSError as error:
            raise _error(
                "encode_failure",
                "The output filesystem cannot provide atomic no-clobber DDS publication.",
                stage="publish_no_clobber",
            ) from error
        published = True

        if not os.path.samefile(temporary, target):
            raise _error(
                "readback_mismatch",
                "DDS publication custody could not be verified.",
            )

        emitted = target.read_bytes()
        _verify_dds_bytes(
            emitted,
            width=int(expected["width"]),
            height=int(expected["height"]),
            pixel_format=str(expected["pixel_format"]),
            mip_count=int(expected["mip_count"]),
        )
        if "sha256:" + hashlib.sha256(emitted).hexdigest() != expected["sha256"]:
            raise _error(
                "readback_mismatch",
                "Emitted DDS checksum does not match the encoder receipt.",
            )
        if retain_custody:
            custody = DDSFileCustody(target=target, guard=temporary)
            return custody
        return None
    except DDSOutputError:
        if published:
            try:
                if os.path.samefile(temporary, target):
                    target.unlink(missing_ok=True)
            except (FileNotFoundError, OSError):
                pass
        raise
    except Exception as error:
        if published:
            try:
                if os.path.samefile(temporary, target):
                    target.unlink(missing_ok=True)
            except (FileNotFoundError, OSError):
                pass
        raise _error(
            "encode_failure",
            "DDS atomic publication failed.",
        ) from error
    finally:
        if custody is None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


__all__ = [
    "DDS_ERROR_SCHEMA",
    "DDS_RECEIPT_SCHEMA",
    "DDSFileCustody",
    "DDSOutputError",
    "MIP_POLICIES",
    "PINNED_PILLOW_REVISION",
    "PIXEL_FORMATS",
    "encode_dds",
    "normalize_tensor_image",
    "read_dds_header",
    "write_dds_atomic",
]
