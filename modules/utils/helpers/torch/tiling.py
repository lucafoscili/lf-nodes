import math
from dataclasses import dataclass
from typing import Iterable, Sequence, Tuple

import torch
import torch.nn.functional as F

@dataclass(frozen=True)
class TileSpec:
    """
    TileSpec defines the coordinates and overlap properties of a rectangular tile within a larger image or grid.

    Attributes:
        x0 (int): The starting x-coordinate of the tile (inclusive).
        x1 (int): The ending x-coordinate of the tile (exclusive).
        y0 (int): The starting y-coordinate of the tile (inclusive).
        y1 (int): The ending y-coordinate of the tile (exclusive).
        inner_x0 (int): The starting x-coordinate of the inner (non-overlapping) region of the tile.
        inner_x1 (int): The ending x-coordinate of the inner (non-overlapping) region of the tile.
        inner_y0 (int): The starting y-coordinate of the inner (non-overlapping) region of the tile.
        inner_y1 (int): The ending y-coordinate of the inner (non-overlapping) region of the tile.

    Properties:
        width (int): The width of the tile (x1 - x0).
        height (int): The height of the tile (y1 - y0).
        left_overlap (int): The width of the overlap on the left side (inner_x0 - x0).
        right_overlap (int): The width of the overlap on the right side (x1 - inner_x1).
        top_overlap (int): The height of the overlap on the top side (inner_y0 - y0).
        bottom_overlap (int): The height of the overlap on the bottom side (y1 - inner_y1).
    """
    x0: int
    x1: int
    y0: int
    y1: int
    inner_x0: int
    inner_x1: int
    inner_y0: int
    inner_y1: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def left_overlap(self) -> int:
        return self.inner_x0 - self.x0

    @property
    def right_overlap(self) -> int:
        return self.x1 - self.inner_x1

    @property
    def top_overlap(self) -> int:
        return self.inner_y0 - self.y0

    @property
    def bottom_overlap(self) -> int:
        return self.y1 - self.inner_y1

@dataclass(frozen=True)
class TilePlan:
    """
    Represents a plan for tiling an image or tensor into smaller sections.

    Attributes:
        tiles (Sequence[TileSpec]): A sequence of TileSpec objects, each describing a single tile's position and size.
        cols (int): The number of columns in the tiling grid.
        rows (int): The number of rows in the tiling grid.
    """
    tiles: Sequence[TileSpec]
    cols: int
    rows: int

def _even_grid_from_tile_count(tile_count: int) -> Tuple[int, int]:
    """
    Calculates the number of columns and rows to arrange a given number of tiles into an even grid.

    Args:
        tile_count (int): The total number of tiles to arrange.

    Returns:
        Tuple[int, int]: A tuple containing the number of columns and rows for the grid.

    Notes:
        - The function tries to create a grid as close to square as possible.
        - The number of columns and rows will always be sufficient to fit all tiles.
    """
    tile_count = max(1, tile_count)
    root = math.sqrt(tile_count)
    cols = max(1, int(round(root)))
    rows = math.ceil(tile_count / cols)
    while cols * rows < tile_count:
        cols += 1

    return cols, rows

def _auto_overlap(stride: int) -> int:
    """
    Calculates an automatic overlap value based on the given stride.

    The overlap is determined as 30% of the stride, but will not be less than 32.

    Args:
        stride (int): The stride value to base the overlap calculation on.

    Returns:
        int: The calculated overlap value, which is at least 32.
    """
    return max(32, int(stride * 0.3))

def plan_input_tiles(width: int, height: int, tile_count: int) -> TilePlan:
    """
    Divides an input area of specified width and height into a grid of tiles, based on the desired tile count.

    The function calculates the optimal number of columns and rows to evenly distribute the tiles,
    determines the stride (size) of each tile, and computes overlaps between adjacent tiles to ensure
    seamless coverage. Each tile's coordinates are specified both for the outer region (including overlap)
    and the inner region (without overlap). When the computed tile size already covers the entire frame,
    the plan collapses to a single tile automatically.

    Args:
        width (int): The width of the input area to be tiled.
        height (int): The height of the input area to be tiled.
        tile_count (int): The total number of tiles to divide the area into.

    Returns:
        TilePlan: An object containing the list of tile specifications, and the number of columns and rows in the grid.
    """
    cols, rows = _even_grid_from_tile_count(tile_count)
    stride_w = math.ceil(width / cols) if cols else width
    stride_h = math.ceil(height / rows) if rows else height

    collapse_to_single = (cols > 1 or rows > 1) and stride_w >= width and stride_h >= height
    if collapse_to_single:
        cols = rows = 1
        stride_w = width
        stride_h = height

    overlap_w = _auto_overlap(stride_w) if cols > 1 else 0
    overlap_h = _auto_overlap(stride_h) if rows > 1 else 0

    tiles = []
    for row in range(rows):
        for col in range(cols):
            inner_x0 = col * stride_w
            inner_y0 = row * stride_h
            inner_x1 = min(width, inner_x0 + stride_w)
            inner_y1 = min(height, inner_y0 + stride_h)

            x0 = max(0, inner_x0 - overlap_w)
            y0 = max(0, inner_y0 - overlap_h)
            x1 = min(width, inner_x1 + overlap_w)
            y1 = min(height, inner_y1 + overlap_h)

            tiles.append(
                TileSpec(
                    x0=x0,
                    x1=x1,
                    y0=y0,
                    y1=y1,
                    inner_x0=inner_x0,
                    inner_x1=inner_x1,
                    inner_y0=inner_y0,
                    inner_y1=inner_y1,
                )
            )

    return TilePlan(tiles=tiles, cols=cols, rows=rows)


def _edge_fade(length: int, device: torch.device) -> torch.Tensor:
    """
    Generates a 1D tensor for edge fading using a squared sine function.

    This function creates a tensor of length `length` where values smoothly transition from 0 to 1,
    following the squared sine curve over the interval [0, pi/2]. This is useful for creating smooth
    fade effects at the edges of an array, such as in image tiling or blending operations.

    Args:
        length (int): The number of elements in the output tensor. If length <= 0, returns an empty tensor.
        device (torch.device): The device on which to create the tensor.

    Returns:
        torch.Tensor: A 1D tensor of shape (length,) containing the edge fade values.
    """
    if length <= 0:
        return torch.ones(0, device=device)
    t = torch.linspace(0.0, math.pi / 2.0, steps=length, device=device)

    return torch.sin(t) ** 2

def make_blend_mask(
    height: int,
    width: int,
    left: int,
    right: int,
    top: int,
    bottom: int,
    device: torch.device,
) -> torch.Tensor:
    """
    Creates a 2D blending mask tensor with smooth fading edges for tiling operations.

    The mask has ones in the center and smoothly fades to zero at the specified edges (top, bottom, left, right).
    The fading is applied using a helper function `_edge_fade` for each edge, and the mask is constructed by
    multiplying the vertical and horizontal fade vectors.

    Args:
        height (int): Height of the mask.
        width (int): Width of the mask.
        left (int): Number of pixels to fade on the left edge.
        right (int): Number of pixels to fade on the right edge.
        top (int): Number of pixels to fade on the top edge.
        bottom (int): Number of pixels to fade on the bottom edge.
        device (torch.device): The device on which to create the mask tensor.

    Returns:
        torch.Tensor: A mask tensor of shape (1, height, width, 1) with values in [0, 1].
    """
    mask_y = torch.ones(height, device=device)
    mask_x = torch.ones(width, device=device)

    if top > 0:
        mask_y[:top] = _edge_fade(top, device)
    if bottom > 0:
        mask_y[-bottom:] = torch.flip(_edge_fade(bottom, device), dims=[0])
    if left > 0:
        mask_x[:left] = _edge_fade(left, device)
    if right > 0:
        mask_x[-right:] = torch.flip(_edge_fade(right, device), dims=[0])

    mask = torch.clamp(mask_y.view(-1, 1) * mask_x.view(1, -1), 0.0, 1.0)

    return mask.view(1, height, width, 1)

def blend_upscaled_tiles(
    upscaled_tiles: Iterable[torch.Tensor],
    specs: Sequence[TileSpec],
    scale: float,
    device: torch.device,
    channels: int,
) -> torch.Tensor:
    """
    Blends a sequence of upscaled image tiles into a single output tensor, using weighted masks to smoothly merge overlapping regions.

    Args:
        upscaled_tiles (Iterable[torch.Tensor]): Iterable of upscaled image tiles as tensors, each with shape (1, H, W, C).
        specs (Sequence[TileSpec]): Sequence of TileSpec objects describing the position and overlap of each tile.
        scale (float): The scaling factor applied to the tile coordinates and overlaps.
        device (torch.device): The device on which to perform tensor operations.
        channels (int): Number of image channels (e.g., 3 for RGB).

    Returns:
        torch.Tensor: The blended output image tensor of shape (1, height, width, channels).
    """
    scale = float(scale)
    width = int(round(max(spec.x1 for spec in specs) * scale))
    height = int(round(max(spec.y1 for spec in specs) * scale))
    canvas = torch.zeros((1, height, width, channels), device=device)
    weights = torch.zeros_like(canvas)

    for tile, spec in zip(upscaled_tiles, specs):
        up_h, up_w = tile.shape[1], tile.shape[2]
        expected_w = int(round((spec.x1 - spec.x0) * scale))
        expected_h = int(round((spec.y1 - spec.y0) * scale))

        if tile.shape[1] != expected_h or tile.shape[2] != expected_w:
            tile = F.interpolate(
                tile.permute(0, 3, 1, 2),
                size=(expected_h, expected_w),
                mode="bicubic",
                align_corners=False,
                antialias=True,
            ).permute(0, 2, 3, 1)

        left = int(round(spec.left_overlap * scale))
        right = int(round(spec.right_overlap * scale))
        top = int(round(spec.top_overlap * scale))
        bottom = int(round(spec.bottom_overlap * scale))

        mask = make_blend_mask(expected_h, expected_w, left, right, top, bottom, device)

        x0 = int(round(spec.x0 * scale))
        y0 = int(round(spec.y0 * scale))
        x1 = x0 + expected_w
        y1 = y0 + expected_h

        canvas[..., y0:y1, x0:x1, :] += tile * mask
        weights[..., y0:y1, x0:x1, :] += mask

    weights = torch.clamp(weights, min=1e-6)

    return canvas / weights
