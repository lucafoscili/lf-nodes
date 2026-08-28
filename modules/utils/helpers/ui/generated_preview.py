from __future__ import annotations

import hashlib
import io
import os
import tempfile
from dataclasses import dataclass

import torch
from PIL import Image

from ...constants import GENERATED_PREVIEW_SUBDIR
from ..api.get_resource_url import get_resource_url
from ..comfy.get_comfy_dir import get_comfy_dir
from ..torch.image_composite import resize_composite_image
from .create_compare_node import create_compare_node
from .create_masonry_node import create_masonry_node


@dataclass(frozen=True)
class GeneratedPreview:
    """A restart-stable, disposable widget preview stored under Comfy input."""

    absolute_path: str
    subfolder: str
    filename: str
    url: str
    sha256: str
    width: int
    height: int
    mode: str


def _prepare_preview_tensor(
    image: torch.Tensor,
    *,
    target_size: tuple[int, int] | None,
    max_long_edge: int,
) -> torch.Tensor:
    if not isinstance(image, torch.Tensor):
        raise TypeError("Generated preview image must be a torch.Tensor.")

    if image.ndim == 3:
        image = image.unsqueeze(0)
    if image.ndim != 4 or image.shape[0] != 1:
        raise ValueError("Generated preview image must contain exactly one HWC image.")
    if image.shape[-1] not in (3, 4):
        raise ValueError("Generated preview image must have RGB or RGBA channels.")
    if image.shape[1] < 1 or image.shape[2] < 1:
        raise ValueError("Generated preview image dimensions must be positive.")

    preview = torch.nan_to_num(
        image.detach().to(dtype=torch.float32),
        nan=0.0,
        posinf=1.0,
        neginf=0.0,
    )

    if target_size is not None:
        if (
            len(target_size) != 2
            or isinstance(target_size[0], bool)
            or isinstance(target_size[1], bool)
            or not isinstance(target_size[0], int)
            or not isinstance(target_size[1], int)
            or target_size[0] < 1
            or target_size[1] < 1
        ):
            raise ValueError("Generated preview target_size must contain two positive integers.")
        target_h, target_w = int(target_size[0]), int(target_size[1])
        if preview.shape[1:3] != (target_h, target_w):
            preview = resize_composite_image(preview, target_h, target_w)

    if isinstance(max_long_edge, bool) or not isinstance(max_long_edge, int):
        raise TypeError("Generated preview max_long_edge must be an integer.")
    if max_long_edge < 0:
        raise ValueError("Generated preview max_long_edge must be zero or positive.")
    if max_long_edge > 0 and max(preview.shape[1:3]) > max_long_edge:
        height, width = preview.shape[1:3]
        scale = max_long_edge / max(height, width)
        target_h = max(1, round(height * scale))
        target_w = max(1, round(width * scale))
        preview = resize_composite_image(preview, target_h, target_w)

    return preview.clamp(0.0, 1.0).to(device="cpu").contiguous()


def _encode_png(image: torch.Tensor) -> tuple[bytes, int, int, str]:
    pixels = (
        image[0]
        .mul(255.0)
        .round()
        .to(dtype=torch.uint8)
        .numpy()
    )
    mode = "RGBA" if pixels.shape[-1] == 4 else "RGB"
    pil_image = Image.fromarray(pixels, mode=mode)
    buffer = io.BytesIO()
    pil_image.save(
        buffer,
        format="PNG",
        optimize=False,
        compress_level=9,
    )
    return buffer.getvalue(), pil_image.width, pil_image.height, mode


def cache_generated_preview(
    image: torch.Tensor,
    *,
    target_size: tuple[int, int] | None = None,
    max_long_edge: int = 512,
) -> GeneratedPreview:
    """Persist one generated widget preview by content hash under Comfy input.

    The resource is a disposable cache, but unlike Comfy temp files it survives a
    restart and can therefore hydrate a saved LF widget without rerunning its node.
    """

    preview = _prepare_preview_tensor(
        image,
        target_size=target_size,
        max_long_edge=max_long_edge,
    )
    png_bytes, width, height, mode = _encode_png(preview)
    digest = hashlib.sha256(png_bytes).hexdigest()
    subfolder = f"{GENERATED_PREVIEW_SUBDIR}/{digest[:2]}"
    filename = f"{digest}.png"

    input_root = os.path.abspath(get_comfy_dir("input"))
    destination_dir = os.path.abspath(
        os.path.join(input_root, *subfolder.split("/"))
    )
    if os.path.commonpath([input_root, destination_dir]) != input_root:
        raise ValueError("Generated preview destination escaped the Comfy input directory.")
    os.makedirs(destination_dir, exist_ok=True)
    destination = os.path.join(destination_dir, filename)

    existing_matches = False
    try:
        with open(destination, "rb") as existing:
            existing_matches = existing.read() == png_bytes
    except FileNotFoundError:
        pass

    if not existing_matches:
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=f".{digest}.",
                suffix=".tmp",
                dir=destination_dir,
                delete=False,
            ) as temporary:
                temporary.write(png_bytes)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = temporary.name
            os.replace(temporary_path, destination)
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)

    return GeneratedPreview(
        absolute_path=destination,
        subfolder=subfolder,
        filename=filename,
        url=get_resource_url(subfolder, filename, "input", cache_bust=False),
        sha256=digest,
        width=width,
        height=height,
        mode=mode,
    )


def create_cached_masonry_node(
    image: torch.Tensor,
    *,
    index: int,
    label: str,
) -> dict:
    """Create one masonry cell backed by a restart-stable generated preview."""

    preview = cache_generated_preview(image)
    return create_masonry_node(label, preview.url, index)


def create_cached_compare_node(
    before: torch.Tensor,
    after: torch.Tensor,
    *,
    index: int,
    title: str | None = None,
    debug: torch.Tensor | None = None,
) -> dict:
    """Create one compare cell backed by restart-stable generated previews."""

    before_preview = cache_generated_preview(before)
    after_preview = cache_generated_preview(after)
    debug_url = cache_generated_preview(debug).url if debug is not None else None
    return create_compare_node(
        before_preview.url,
        after_preview.url,
        index,
        title=title,
        debug=debug_url,
    )
