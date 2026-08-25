from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.api import get_resource_url
from ...utils.helpers.comfy import resolve_filepath, safe_send_sync
from ...utils.helpers.conversion import tensor_to_pil
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch.image_composite import (
    MAX_COMPOSITE_PIXELS,
    promote_to_rgba,
    render_label_chip,
    resize_composite_image,
    validate_composite_image,
    validate_composite_integer,
)


GRID_RECEIPT_SCHEMA = "lf.image_grid.receipt.v1"
GRID_BACKGROUNDS = ["black", "white", "transparent"]
_MAX_TITLE_LENGTH = 128
_MAX_HEADER_LENGTH = 64
# Retain the module-local guard seam used by focused allocation-safety tests.
_MAX_OUTPUT_PIXELS = MAX_COMPOSITE_PIXELS


def _normalize_text(value: Any, *, maximum: int) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").strip()[:maximum]


def _json_copy(value: Any, field: str) -> Any:
    try:
        return json.loads(
            json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must contain valid JSON values.") from error


def _unwrap_dataset(value: Any) -> Any:
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def _automatic_dataset(image_count: int) -> dict:
    return {
        "columns": [
            {"id": f"image_{index + 1}", "title": str(index + 1)}
            for index in range(image_count)
        ],
        "nodes": [{"id": "row_1", "value": ""}],
    }


def _parse_matrix_dataset(value: Any, image_count: int) -> dict:
    """Validate a flat LfDataDataset whose columns/nodes define the image matrix."""
    value = _unwrap_dataset(value)
    if value is None or value == "" or value == {}:
        return _automatic_dataset(image_count)
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError("dataset must be valid JSON.") from error
    if not isinstance(value, dict):
        raise ValueError("dataset must be an LfDataDataset object.")

    matrix = _json_copy(value, "dataset")
    columns = matrix.get("columns")
    nodes = matrix.get("nodes")
    if not isinstance(columns, list) or not columns:
        raise ValueError("dataset.columns must be a non-empty array.")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("dataset.nodes must be a non-empty array.")

    column_ids: list[str] = []
    for index, column in enumerate(columns):
        if not isinstance(column, dict):
            raise ValueError(f"dataset.columns[{index}] must be an object.")
        column_id = column.get("id")
        title = column.get("title")
        if not isinstance(column_id, str) or not column_id.strip():
            raise ValueError(f"dataset.columns[{index}].id must be a non-empty string.")
        if column_id in column_ids:
            raise ValueError(f"dataset column id '{column_id}' is duplicated.")
        if not isinstance(title, str):
            raise ValueError(f"dataset.columns[{index}].title must be a string.")
        column_ids.append(column_id)

    node_ids: set[str] = set()
    for row, node in enumerate(nodes):
        if not isinstance(node, dict):
            raise ValueError(f"dataset.nodes[{row}] must be an object.")
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id.strip():
            raise ValueError(f"dataset.nodes[{row}].id must be a non-empty string.")
        if node_id in node_ids:
            raise ValueError(f"dataset node id '{node_id}' is duplicated.")
        node_ids.add(node_id)
        if node.get("children"):
            raise ValueError("dataset.nodes must be flat; child nodes cannot form a matrix row.")
        value_field = node.get("value", node_id)
        if not isinstance(value_field, (str, int, float)):
            raise ValueError(
                f"dataset.nodes[{row}].value must be a string or number."
            )
        cells = node.get("cells", {})
        if not isinstance(cells, dict):
            raise ValueError(f"dataset.nodes[{row}].cells must be an object.")
        unknown_cells = sorted(set(cells) - set(column_ids))
        if unknown_cells:
            raise ValueError(
                f"dataset.nodes[{row}].cells contains unknown column(s): "
                + ", ".join(unknown_cells)
            )
        for column_id, cell in cells.items():
            if not isinstance(cell, dict):
                raise ValueError(
                    f"dataset.nodes[{row}].cells.{column_id} must be an object."
                )
            html_props = cell.get("htmlProps")
            if html_props is not None and not isinstance(html_props, dict):
                raise ValueError(
                    f"dataset.nodes[{row}].cells.{column_id}.htmlProps must be an object."
                )
        if "cells" in node:
            node["cells"] = cells

    expected_images = len(columns) * len(nodes)
    if image_count != expected_images:
        raise ValueError(
            f"dataset defines a {len(nodes)}x{len(columns)} matrix and therefore "
            f"requires exactly {expected_images} images; received {image_count}."
        )
    return matrix


def _fit_dimensions(
    source_width: int,
    source_height: int,
    cell_width: int,
    cell_height: int,
) -> tuple[int, int]:
    if source_width * cell_height >= source_height * cell_width:
        target_width = cell_width
        target_height = max(
            1,
            (source_height * cell_width + source_width // 2) // source_width,
        )
    else:
        target_height = cell_height
        target_width = max(
            1,
            (source_width * cell_height + source_height // 2) // source_height,
        )
    return target_width, target_height


def _background_canvas(
    *,
    height: int,
    width: int,
    channels: int,
    background: str,
    device: torch.device,
) -> torch.Tensor:
    canvas = torch.zeros((1, height, width, channels), device=device)
    if background == "white":
        canvas[..., :3] = 1.0
    if channels == 4 and background != "transparent":
        canvas[..., 3] = 1.0
    return canvas


def _paint_opaque_black(
    canvas: torch.Tensor,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    canvas[:, y : y + height, x : x + width, :3] = 0.0
    if canvas.shape[-1] == 4:
        canvas[:, y : y + height, x : x + width, 3] = 1.0


def compose_image_grid(
    image: Any,
    *,
    dataset: Any = None,
    title: str = "",
    cell_width: int = 512,
    cell_height: int = 512,
    gap_px: int = 8,
    background: str = "black",
    show_headers: bool = True,
) -> tuple[torch.Tensor, dict, dict]:
    """Render an ordered image list using an LfDataDataset as its matrix schema."""
    images = normalize_input_image(image)
    if not images:
        raise ValueError("image must contain at least one image.")

    cell_width = validate_composite_integer(cell_width, "cell_width", minimum=32)
    cell_height = validate_composite_integer(cell_height, "cell_height", minimum=32)
    gap_px = validate_composite_integer(gap_px, "gap_px", minimum=0)
    if cell_width > 4096 or cell_height > 4096:
        raise ValueError("cell_width and cell_height must be less than or equal to 4096.")
    if gap_px > 1024:
        raise ValueError("gap_px must be less than or equal to 1024.")
    if background not in GRID_BACKGROUNDS:
        raise ValueError(
            "background must be one of: " + ", ".join(GRID_BACKGROUNDS) + "."
        )
    if not isinstance(show_headers, bool):
        raise ValueError("show_headers must be a boolean.")
    if not isinstance(title, str):
        raise ValueError("title must be a string.")
    title = _normalize_text(title, maximum=_MAX_TITLE_LENGTH)

    validated: list[torch.Tensor] = []
    device: torch.device | None = None
    for index, candidate in enumerate(images):
        normalized = validate_composite_image(candidate, f"image[{index}]")
        if normalized.shape[0] != 1:
            raise ValueError(f"image[{index}] must contain exactly one image.")
        if device is None:
            device = normalized.device
        validated.append(normalized.to(device=device))
    assert device is not None

    matrix = _parse_matrix_dataset(dataset, len(validated))
    columns = matrix["columns"]
    nodes = matrix["nodes"]
    column_count = len(columns)
    row_count = len(nodes)
    output_channels = (
        4
        if background == "transparent"
        or any(candidate.shape[-1] == 4 for candidate in validated)
        else 3
    )

    column_chips: list[torch.Tensor | None] = []
    row_chips: list[torch.Tensor | None] = []
    column_header_height = 0
    row_header_width = 0
    if show_headers:
        column_chips = [
            render_label_chip(
                _normalize_text(
                    column["title"] or column["id"],
                    maximum=_MAX_HEADER_LENGTH,
                ),
                max_width=max(1, cell_width - 16),
                max_height=cell_height,
                channels=output_channels,
            )
            for column in columns
        ]
        row_chips = [
            render_label_chip(
                _normalize_text(
                    node.get("value") or node["id"],
                    maximum=_MAX_HEADER_LENGTH,
                ),
                max_width=cell_width,
                max_height=cell_height,
                channels=output_channels,
            )
            for node in nodes
        ]
        column_header_height = max(
            (int(chip.shape[0]) for chip in column_chips if chip is not None),
            default=16,
        ) + 16
        row_header_width = max(
            (int(chip.shape[1]) for chip in row_chips if chip is not None),
            default=16,
        ) + 16

    matrix_width = column_count * cell_width + (column_count - 1) * gap_px
    matrix_height = row_count * cell_height + (row_count - 1) * gap_px
    row_header_gap = gap_px if row_header_width else 0
    column_header_gap = gap_px if column_header_height else 0
    body_width = row_header_width + row_header_gap + matrix_width
    body_height = column_header_height + column_header_gap + matrix_height

    title_chip = None
    title_height = 0
    if title:
        title_chip = render_label_chip(
            title,
            max_width=max(1, body_width - 32),
            max_height=max(64, cell_height),
            channels=output_channels,
        )
        if title_chip is not None:
            title_height = int(title_chip.shape[0]) + 24
    title_gap = gap_px if title_height else 0
    grid_height = title_height + title_gap + body_height
    grid_width = body_width
    if grid_width * grid_height > _MAX_OUTPUT_PIXELS:
        raise ValueError(
            "LF_ImageGrid output exceeds the 64-megapixel safety limit; reduce "
            "the matrix or cell dimensions."
        )

    grid = _background_canvas(
        height=grid_height,
        width=grid_width,
        channels=output_channels,
        background=background,
        device=device,
    )
    if title_height:
        _paint_opaque_black(
            grid,
            x=0,
            y=0,
            width=grid_width,
            height=title_height,
        )
        assert title_chip is not None
        title_chip = title_chip.to(device=device, dtype=grid.dtype)
        title_y = (title_height - int(title_chip.shape[0])) // 2
        title_x = (grid_width - int(title_chip.shape[1])) // 2
        grid[
            :,
            title_y : title_y + title_chip.shape[0],
            title_x : title_x + title_chip.shape[1],
            :,
        ] = title_chip.unsqueeze(0)

    header_y = title_height + title_gap
    matrix_x = row_header_width + row_header_gap
    matrix_y = header_y + column_header_height + column_header_gap
    if column_header_height:
        for column, chip in enumerate(column_chips):
            x = matrix_x + column * (cell_width + gap_px)
            _paint_opaque_black(
                grid,
                x=x,
                y=header_y,
                width=cell_width,
                height=column_header_height,
            )
            if chip is not None:
                chip = chip.to(device=device, dtype=grid.dtype)
                chip_x = x + (cell_width - int(chip.shape[1])) // 2
                chip_y = header_y + (column_header_height - int(chip.shape[0])) // 2
                grid[
                    :,
                    chip_y : chip_y + chip.shape[0],
                    chip_x : chip_x + chip.shape[1],
                    :,
                ] = chip.unsqueeze(0)

    if row_header_width:
        for row, chip in enumerate(row_chips):
            y = matrix_y + row * (cell_height + gap_px)
            _paint_opaque_black(
                grid,
                x=0,
                y=y,
                width=row_header_width,
                height=cell_height,
            )
            if chip is not None:
                chip = chip.to(device=device, dtype=grid.dtype)
                chip_x = (row_header_width - int(chip.shape[1])) // 2
                chip_y = y + (cell_height - int(chip.shape[0])) // 2
                grid[
                    :,
                    chip_y : chip_y + chip.shape[0],
                    chip_x : chip_x + chip.shape[1],
                    :,
                ] = chip.unsqueeze(0)

    receipt_items: list[dict] = []
    for index, source in enumerate(validated):
        row = index // column_count
        column = index % column_count
        cell_x = matrix_x + column * (cell_width + gap_px)
        cell_y = matrix_y + row * (cell_height + gap_px)
        source_height = int(source.shape[1])
        source_width = int(source.shape[2])
        source_channels = int(source.shape[3])
        target_width, target_height = _fit_dimensions(
            source_width,
            source_height,
            cell_width,
            cell_height,
        )
        if output_channels == 4:
            source = promote_to_rgba(source)
        resized = resize_composite_image(source, target_height, target_width)
        image_x = cell_x + (cell_width - target_width) // 2
        image_y = cell_y + (cell_height - target_height) // 2
        grid[
            :,
            image_y : image_y + target_height,
            image_x : image_x + target_width,
            :,
        ] = resized

        receipt_items.append(
            {
                "index": index,
                "row": row,
                "column": column,
                "nodeId": nodes[row]["id"],
                "columnId": columns[column]["id"],
                "source": {
                    "width": source_width,
                    "height": source_height,
                    "channels": source_channels,
                },
                "placement": {
                    "x": image_x,
                    "y": image_y,
                    "width": target_width,
                    "height": target_height,
                },
            }
        )

    receipt = {
        "schema": GRID_RECEIPT_SCHEMA,
        "title": title,
        "imageCount": len(validated),
        "layout": {
            "columns": column_count,
            "rows": row_count,
            "cellWidth": cell_width,
            "cellHeight": cell_height,
            "columnHeaderHeight": column_header_height,
            "rowHeaderWidth": row_header_width,
            "titleHeight": title_height,
            "gapPx": gap_px,
            "background": background,
            "showHeaders": show_headers,
            "fit": "contain",
            "resizeFilter": "bicubic_antialiased",
            "alphaResize": "premultiplied",
        },
        "output": {
            "width": grid_width,
            "height": grid_height,
            "channels": output_channels,
        },
        "items": receipt_items,
    }
    return grid, matrix, receipt


def _populate_image_cells(
    matrix: dict,
    images: list[torch.Tensor],
    *,
    resolve_image,
) -> dict:
    populated = deepcopy(matrix)
    columns = populated["columns"]
    for index, image in enumerate(images):
        row = index // len(columns)
        column = index % len(columns)
        node = populated["nodes"][row]
        column_id = columns[column]["id"]
        url, filename = resolve_image(image, row, column)
        existing = node.setdefault("cells", {}).get(column_id, {})
        html_props = dict(existing.get("htmlProps") or {})
        html_props.setdefault("id", f"{node['id']}:{column_id}")
        html_props.setdefault(
            "title",
            f"{node.get('value') or node['id']} · {columns[column]['title'] or column_id}",
        )
        node["cells"][column_id] = {
            **existing,
            "shape": "image",
            "value": url,
            "lfValue": url,
            "htmlProps": html_props,
        }
    for node in populated["nodes"]:
        populated_cells = node["cells"]
        node["cells"] = {
            column["id"]: populated_cells[column["id"]] for column in columns
        }
    return populated


# region LF_ImageGrid
class LF_ImageGrid:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": "Images in row-major order. The LfDataDataset columns define matrix columns and nodes define rows."
                    },
                ),
                "cell_width": (
                    Input.INTEGER,
                    {
                        "default": 512,
                        "min": 32,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "Width of every comparison cell. Images are fitted without cropping or stretching.",
                    },
                ),
                "cell_height": (
                    Input.INTEGER,
                    {
                        "default": 512,
                        "min": 32,
                        "max": 4096,
                        "step": 8,
                        "tooltip": "Height of every comparison cell. Images are centered and letterboxed when needed.",
                    },
                ),
                "gap_px": (
                    Input.INTEGER,
                    {
                        "default": 8,
                        "min": 0,
                        "max": 1024,
                        "step": 1,
                        "tooltip": "Spacing between matrix cells and headers, in pixels.",
                    },
                ),
                "background": (
                    GRID_BACKGROUNDS,
                    {
                        "default": "black",
                        "tooltip": "Letterbox and gap background. Transparent produces RGBA output.",
                    },
                ),
                "show_headers": (
                    Input.BOOLEAN,
                    {
                        "default": True,
                        "tooltip": "Render column titles above the matrix and node values beside each row.",
                    },
                ),
                "title": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": "Optional title rendered above the complete comparison matrix.",
                    },
                ),
            },
            "optional": {
                "dataset": (
                    Input.JSON,
                    {
                        "tooltip": "LfDataDataset from LF_WriteJSON. Columns are the horizontal axis, nodes are rows, and the node fills their cells with the ordered images. Omit for one automatic row."
                    },
                ),
                "ui_widget": (Input.LF_MASONRY, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Rendered comparison matrix.",
        "LfDataDataset whose cells are the images that compose the matrix.",
        "lf.image_grid.receipt.v1 layout receipt.",
    )
    RETURN_NAMES = ("image", "dataset", "receipt")
    RETURN_TYPES = (Input.IMAGE, Input.JSON, Input.JSON)

    def on_exec(self, **kwargs: dict) -> dict:
        self._temp_cache.cleanup()
        raw_images = kwargs.get("image")
        grid, matrix, receipt = compose_image_grid(
            raw_images,
            dataset=kwargs.get("dataset"),
            title=normalize_list_to_value(kwargs.get("title", "")),
            cell_width=normalize_list_to_value(kwargs.get("cell_width", 512)),
            cell_height=normalize_list_to_value(kwargs.get("cell_height", 512)),
            gap_px=normalize_list_to_value(kwargs.get("gap_px", 8)),
            background=normalize_list_to_value(kwargs.get("background", "black")),
            show_headers=normalize_list_to_value(kwargs.get("show_headers", True)),
        )
        images = [
            validate_composite_image(candidate, f"image[{index}]")
            for index, candidate in enumerate(normalize_input_image(raw_images))
        ]

        def resolve_image(image: torch.Tensor, row: int, column: int):
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix=f"image_grid_{row + 1}_{column + 1}",
                image=image,
                temp_cache=self._temp_cache,
            )
            tensor_to_pil(image).save(output_file, format="PNG")
            return get_resource_url(subfolder, filename, "temp"), filename

        populated = _populate_image_cells(
            matrix,
            images,
            resolve_image=resolve_image,
        )
        column_count = len(populated["columns"])
        payload = {
            "columns": column_count,
            "dataset": populated,
            "receipt": receipt,
        }
        node_id = normalize_list_to_value(kwargs.get("node_id"))
        safe_send_sync("imagegrid", payload, node_id)
        return {
            "ui": {"lf_output": [payload]},
            "result": (grid, populated, receipt),
        }


# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImageGrid": LF_ImageGrid,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageGrid": "Image grid",
}
# endregion
