from __future__ import annotations

from types import SimpleNamespace

from PIL import Image
import pytest
import torch

from modules.nodes.image import image_grid as image_grid_module


def _solid(
    height: int,
    width: int,
    color: tuple[float, ...],
    *,
    batch: int = 1,
) -> torch.Tensor:
    image = torch.zeros(batch, height, width, len(color), dtype=torch.float32)
    for channel, value in enumerate(color):
        image[..., channel] = value
    return image


def _matrix_2x2() -> dict:
    return {
        "columns": [
            {"id": "low", "title": "Low"},
            {"id": "high", "title": "High"},
        ],
        "nodes": [
            {"id": "sample_a", "value": "Sample A"},
            {"id": "sample_b", "value": "Sample B"},
        ],
    }


def test_matrix_dataset_places_images_row_major_with_exact_geometry() -> None:
    images = torch.cat(
        (
            _solid(32, 32, (1.0, 0.0, 0.0)),
            _solid(32, 32, (0.0, 1.0, 0.0)),
            _solid(32, 32, (0.0, 0.0, 1.0)),
            _solid(32, 32, (1.0, 1.0, 0.0)),
        ),
        dim=0,
    )

    grid, matrix, receipt = image_grid_module.compose_image_grid(
        images,
        dataset=_matrix_2x2(),
        cell_width=32,
        cell_height=32,
        gap_px=2,
        show_headers=False,
    )

    assert grid.shape == (1, 66, 66, 3)
    torch.testing.assert_close(grid[0, 16, 16], torch.tensor([1.0, 0.0, 0.0]))
    torch.testing.assert_close(grid[0, 16, 50], torch.tensor([0.0, 1.0, 0.0]))
    torch.testing.assert_close(grid[0, 50, 16], torch.tensor([0.0, 0.0, 1.0]))
    torch.testing.assert_close(grid[0, 50, 50], torch.tensor([1.0, 1.0, 0.0]))
    assert torch.count_nonzero(grid[:, :, 32:34]) == 0
    assert torch.count_nonzero(grid[:, 32:34, :]) == 0
    assert [item["nodeId"] for item in receipt["items"]] == [
        "sample_a",
        "sample_a",
        "sample_b",
        "sample_b",
    ]
    assert [item["columnId"] for item in receipt["items"]] == [
        "low",
        "high",
        "low",
        "high",
    ]
    assert matrix == _matrix_2x2()


def test_mixed_aspect_ratios_are_contained_and_centered() -> None:
    matrix = {
        "columns": [
            {"id": "landscape", "title": "Landscape"},
            {"id": "portrait", "title": "Portrait"},
        ],
        "nodes": [{"id": "row", "value": "Sample"}],
    }
    images = [
        _solid(8, 16, (1.0, 0.0, 0.0)),
        _solid(16, 8, (0.0, 1.0, 0.0)),
    ]

    grid, _, _ = image_grid_module.compose_image_grid(
        images,
        dataset=matrix,
        cell_width=32,
        cell_height=32,
        gap_px=0,
        show_headers=False,
    )

    assert grid.shape == (1, 32, 64, 3)
    assert torch.count_nonzero(grid[:, :8, :32]) == 0
    torch.testing.assert_close(
        grid[:, 8:24, :32], _solid(16, 32, (1.0, 0.0, 0.0))
    )
    assert torch.count_nonzero(grid[:, 24:, :32]) == 0
    assert torch.count_nonzero(grid[:, :, 32:40]) == 0
    torch.testing.assert_close(
        grid[:, :, 40:56], _solid(32, 16, (0.0, 1.0, 0.0))
    )
    assert torch.count_nonzero(grid[:, :, 56:]) == 0


def test_headers_and_title_are_deterministic_and_occupy_separate_bands() -> None:
    images = _solid(32, 32, (0.0, 0.0, 0.0), batch=4)
    options = {
        "dataset": _matrix_2x2(),
        "title": "Parameter comparison",
        "cell_width": 64,
        "cell_height": 64,
        "gap_px": 4,
        "show_headers": True,
    }

    first, _, receipt = image_grid_module.compose_image_grid(images, **options)
    second, _, _ = image_grid_module.compose_image_grid(images, **options)

    torch.testing.assert_close(first, second)
    layout = receipt["layout"]
    assert layout["columnHeaderHeight"] > 0
    assert layout["rowHeaderWidth"] > 0
    assert layout["titleHeight"] > 0
    assert float(first[:, : layout["titleHeight"], :, :3].max()) > 0.5
    header_y = layout["titleHeight"] + layout["gapPx"]
    assert (
        float(
            first[
                :,
                header_y : header_y + layout["columnHeaderHeight"],
                :,
                :3,
            ].max()
        )
        > 0.5
    )


def test_omitted_dataset_builds_one_lf_dataset_row() -> None:
    grid, matrix, receipt = image_grid_module.compose_image_grid(
        _solid(32, 32, (0.25, 0.5, 0.75), batch=3),
        cell_width=32,
        cell_height=32,
        gap_px=1,
        show_headers=False,
    )

    assert grid.shape == (1, 32, 98, 3)
    assert [column["id"] for column in matrix["columns"]] == [
        "image_1",
        "image_2",
        "image_3",
    ]
    assert matrix["nodes"] == [{"id": "row_1", "value": ""}]
    assert receipt["layout"]["columns"] == 3
    assert receipt["layout"]["rows"] == 1


def test_raster_label_normalization_does_not_mutate_dataset_metadata() -> None:
    long_title = "Column\n" + "x" * 80
    matrix = {
        "columns": [{"id": "amount", "title": long_title}],
        "nodes": [{"id": "row", "value": 0.75, "description": "Preserve me"}],
    }

    _, returned, _ = image_grid_module.compose_image_grid(
        _solid(32, 32, (0.25, 0.5, 0.75)),
        dataset=matrix,
        cell_width=32,
        cell_height=32,
        show_headers=True,
    )

    assert returned == matrix
    assert returned["columns"][0]["title"] == long_title
    assert returned["nodes"][0]["value"] == 0.75


def test_transparent_background_promotes_rgb_and_preserves_rgba() -> None:
    matrix = {
        "columns": [
            {"id": "a", "title": "A"},
            {"id": "b", "title": "B"},
        ],
        "nodes": [{"id": "row", "value": "Row"}],
    }
    images = [
        _solid(32, 32, (1.0, 0.0, 0.0)),
        _solid(32, 32, (0.0, 1.0, 0.0, 0.25)),
    ]

    grid, _, receipt = image_grid_module.compose_image_grid(
        images,
        dataset=matrix,
        cell_width=32,
        cell_height=32,
        gap_px=2,
        background="transparent",
        show_headers=False,
    )

    assert grid.shape == (1, 32, 66, 4)
    torch.testing.assert_close(grid[..., :32, 3], torch.ones(1, 32, 32))
    torch.testing.assert_close(grid[..., 32:34, 3], torch.zeros(1, 32, 2))
    torch.testing.assert_close(grid[..., 34:, 3], torch.full((1, 32, 32), 0.25))
    assert receipt["output"]["channels"] == 4


def test_dataset_shape_and_image_count_fail_closed() -> None:
    with pytest.raises(ValueError, match="requires exactly 4 images; received 3"):
        image_grid_module.compose_image_grid(
            _solid(32, 32, (0.0, 0.0, 0.0), batch=3),
            dataset=_matrix_2x2(),
            cell_width=32,
            cell_height=32,
        )

    duplicate_columns = _matrix_2x2()
    duplicate_columns["columns"][1]["id"] = "low"
    with pytest.raises(ValueError, match="column id 'low' is duplicated"):
        image_grid_module.compose_image_grid(
            _solid(32, 32, (0.0, 0.0, 0.0), batch=4),
            dataset=duplicate_columns,
            cell_width=32,
            cell_height=32,
        )

    unknown_cell = _matrix_2x2()
    unknown_cell["nodes"][0]["cells"] = {"missing": {}}
    with pytest.raises(ValueError, match="contains unknown column"):
        image_grid_module.compose_image_grid(
            _solid(32, 32, (0.0, 0.0, 0.0), batch=4),
            dataset=unknown_cell,
            cell_width=32,
            cell_height=32,
        )


def test_output_safety_limit_is_checked_before_allocation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(image_grid_module, "_MAX_OUTPUT_PIXELS", 100)
    with pytest.raises(ValueError, match="64-megapixel safety limit"):
        image_grid_module.compose_image_grid(
            _solid(32, 32, (0.0, 0.0, 0.0)),
            cell_width=32,
            cell_height=32,
            show_headers=False,
        )


def test_node_populates_lf_dataset_cells_and_publishes_masonry_history(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    node = image_grid_module.LF_ImageGrid()
    saved_paths = []

    def cache_generated_preview(image):
        path = tmp_path / f"preview_{len(saved_paths)}.png"
        saved_paths.append(path)
        pixels = image[0].clamp(0, 1).mul(255).round().to(torch.uint8).numpy()
        Image.fromarray(pixels).save(path, format="PNG")
        return SimpleNamespace(
            url=f"/view?filename={path.name}&type=input&subfolder=preview",
        )

    sent = []
    monkeypatch.setattr(
        image_grid_module,
        "cache_generated_preview",
        cache_generated_preview,
    )
    monkeypatch.setattr(
        image_grid_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    matrix = _matrix_2x2()
    matrix["nodes"][0]["cells"] = {
        "high": {"description": "Pre-existing high cell"},
        "low": {"htmlProps": {"title": "Pinned cell title"}},
    }

    response = node.on_exec(
        image=[_solid(32, 32, (0.2, 0.4, 0.6), batch=4)],
        dataset=[matrix],
        cell_width=[32],
        cell_height=[32],
        gap_px=[1],
        background=["black"],
        show_headers=[False],
        title=[""],
        node_id=["grid-node"],
    )

    grid, populated, receipt, image_list = response["result"]
    payload = response["ui"]["lf_output"][0]
    assert grid.shape == (1, 65, 65, 3)
    assert len(image_list) == 1
    assert torch.equal(image_list[0], grid)
    assert payload["columns"] == 2
    assert payload["dataset"] is populated
    assert payload["receipt"] is receipt
    assert receipt["schema"] == "lf.image_grid.receipt.v1"
    cells = [
        populated["nodes"][row]["cells"][column]
        for row in range(2)
        for column in ("low", "high")
    ]
    assert all(cell["shape"] == "image" for cell in cells)
    assert all("type=input" in cell["value"] for cell in cells)
    assert cells[0]["htmlProps"]["title"] == "Pinned cell title"
    assert cells[1]["description"] == "Pre-existing high cell"
    assert all(list(node["cells"]) == ["low", "high"] for node in populated["nodes"])
    assert sent == [("imagegrid", payload, "grid-node")]
    assert len(saved_paths) == 4
    for path in saved_paths:
        with Image.open(path) as preview:
            assert preview.mode == "RGB"
            assert preview.size == (32, 32)


def test_public_schema_and_mapping_use_lf_dataset_vocabulary() -> None:
    schema = image_grid_module.LF_ImageGrid.INPUT_TYPES()

    assert set(schema["required"]) == {
        "image",
        "cell_width",
        "cell_height",
        "gap_px",
        "background",
        "show_headers",
        "title",
    }
    assert schema["optional"]["dataset"][0] == "JSON"
    assert schema["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert image_grid_module.LF_ImageGrid.INPUT_IS_LIST is True
    assert image_grid_module.LF_ImageGrid.RETURN_TYPES == (
        "IMAGE",
        "JSON",
        "JSON",
        "IMAGE",
    )
    assert image_grid_module.LF_ImageGrid.RETURN_NAMES == (
        "image",
        "dataset",
        "receipt",
        "image_list",
    )
    assert image_grid_module.LF_ImageGrid.OUTPUT_IS_LIST == (
        False,
        False,
        False,
        True,
    )
    assert image_grid_module.NODE_CLASS_MAPPINGS == {
        "LF_ImageGrid": image_grid_module.LF_ImageGrid,
    }
    public_contract = repr(schema).lower()
    assert "lora" not in public_contract
    assert "velora" not in public_contract
    assert "stellaris" not in public_contract
