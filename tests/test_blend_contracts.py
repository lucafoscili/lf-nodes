"""Isolated behavior tests for LF_Blend pairing and durable history."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from urllib.parse import parse_qs, urlparse
import sys
import uuid

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]


def _attach(name: str, module: ModuleType) -> ModuleType:
    sys.modules[name] = module
    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent = sys.modules.get(parent_name)
        if parent is not None:
            setattr(parent, child_name, module)
    return module


def _package(name: str) -> ModuleType:
    package = ModuleType(name)
    package.__path__ = []
    return _attach(name, package)


def _module(name: str, **attributes) -> ModuleType:
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    return _attach(name, module)


def _load_source(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    _attach(name, module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def blend_harness(tmp_path: Path):
    prefix = f"_lf_blend_contract_{uuid.uuid4().hex}"
    input_root = tmp_path / "input"
    input_root.mkdir()
    pairs = []
    sent = []

    _package(prefix)
    _package(f"{prefix}.nodes")
    node_filters = _package(f"{prefix}.nodes.filters")
    node_filters.CATEGORY = "test/filters"
    _package(f"{prefix}.utils")
    _package(f"{prefix}.utils.helpers")
    _package(f"{prefix}.utils.helpers.torch")
    ui_package = _package(f"{prefix}.utils.helpers.ui")

    class Input:
        IMAGE = "IMAGE"
        FLOAT = "FLOAT"
        LF_COMPARE = "LF_COMPARE"

    _module(
        f"{prefix}.utils.constants",
        FUNCTION="on_exec",
        Input=Input,
        BLEND_MODE_COMBO=("normal", "screen"),
        GENERATED_PREVIEW_SUBDIR="_lf_external_previews/generated/v1",
    )

    normalize_input_image = _load_source(
        f"{prefix}._normalize_input_image",
        ROOT / "modules" / "utils" / "helpers" / "logic" / "normalize_input_image.py",
    ).normalize_input_image
    normalize_output_image = _load_source(
        f"{prefix}._normalize_output_image",
        ROOT / "modules" / "utils" / "helpers" / "logic" / "normalize_output_image.py",
    ).normalize_output_image

    def normalize_list_to_value(value):
        return value[0] if isinstance(value, list) and value else value

    _module(
        f"{prefix}.utils.helpers.logic",
        normalize_input_image=normalize_input_image,
        normalize_list_to_value=normalize_list_to_value,
        normalize_output_image=normalize_output_image,
    )

    def blend_effect(image, *, overlay_image, alpha_mask, mode):
        pairs.append(
            (
                float(image[0, 0, 0, 0]),
                float(overlay_image[0, 0, 0, 0]),
                alpha_mask,
                mode,
            )
        )
        return image + overlay_image

    _module(f"{prefix}.utils.filters", blend_effect=blend_effect)

    def safe_send_sync(event, payload, node_id=None):
        sent.append((event, payload, node_id))

    comfy_package = _package(f"{prefix}.utils.helpers.comfy")
    comfy_package.safe_send_sync = safe_send_sync
    _module(
        f"{prefix}.utils.helpers.comfy.get_comfy_dir",
        get_comfy_dir=lambda kind: str(input_root),
    )

    def get_resource_url(
        subfolder: str,
        filename: str,
        resource_type: str = "output",
        *,
        cache_bust: bool = True,
    ) -> str:
        url = (
            f"/view?filename={filename}&type={resource_type}"
            f"&subfolder={subfolder}"
        )
        return f"{url}&nonce=test" if cache_bust else url

    _package(f"{prefix}.utils.helpers.api")
    _module(
        f"{prefix}.utils.helpers.api.get_resource_url",
        get_resource_url=get_resource_url,
    )
    _module(
        f"{prefix}.utils.helpers.torch.image_composite",
        resize_composite_image=lambda image, _height, _width: image,
    )
    _load_source(
        f"{prefix}.utils.helpers.ui.create_compare_node",
        ROOT / "modules" / "utils" / "helpers" / "ui" / "create_compare_node.py",
    )
    _load_source(
        f"{prefix}.utils.helpers.ui.create_masonry_node",
        ROOT / "modules" / "utils" / "helpers" / "ui" / "create_masonry_node.py",
    )
    preview_module = _load_source(
        f"{prefix}.utils.helpers.ui.generated_preview",
        ROOT / "modules" / "utils" / "helpers" / "ui" / "generated_preview.py",
    )
    ui_package.create_cached_compare_node = preview_module.create_cached_compare_node

    blend_module = _load_source(
        f"{prefix}.nodes.filters.blend",
        ROOT / "modules" / "nodes" / "filters" / "blend.py",
    )
    harness = SimpleNamespace(
        module=blend_module,
        pairs=pairs,
        sent=sent,
        input_root=input_root,
    )

    yield harness

    for name in list(sys.modules):
        if name == prefix or name.startswith(f"{prefix}."):
            sys.modules.pop(name, None)


def _batch(values: list[float]) -> torch.Tensor:
    return torch.stack(
        [torch.full((2, 3, 3), value, dtype=torch.float32) for value in values]
    )


def _pair_values(harness) -> list[tuple[float, float]]:
    return [(base, overlay) for base, overlay, _, _ in harness.pairs]


def _assert_pair_values(harness, expected: list[tuple[float, float]]) -> None:
    actual = _pair_values(harness)
    assert [pair[0] for pair in actual] == pytest.approx(
        [pair[0] for pair in expected]
    )
    assert [pair[1] for pair in actual] == pytest.approx(
        [pair[1] for pair in expected]
    )


def _output_values(response) -> list[float]:
    _, image_list = response["result"]
    return [float(image[0, 0, 0, 0]) for image in image_list]


def test_equal_batches_pair_by_position_and_preserve_output_order(
    blend_harness,
) -> None:
    assert blend_harness.module.LF_Blend.INPUT_IS_LIST is True
    response = blend_harness.module.LF_Blend().on_exec(
        image=_batch([0.1, 0.2, 0.3]),
        overlay_image=_batch([0.01, 0.02, 0.03]),
        opacity=[0.4],
        blend_mode=["screen"],
    )

    _assert_pair_values(
        blend_harness,
        [(0.1, 0.01), (0.2, 0.02), (0.3, 0.03)]
    )
    assert [call[2:] for call in blend_harness.pairs] == [
        (0.4, "screen"),
        (0.4, "screen"),
        (0.4, "screen"),
    ]
    assert _output_values(response) == pytest.approx([0.11, 0.22, 0.33])
    result = response["result"]
    torch.testing.assert_close(result[0], torch.cat(result[1], dim=0))


def test_single_overlay_broadcasts_across_ordered_base_batch(blend_harness) -> None:
    response = blend_harness.module.LF_Blend().on_exec(
        image=_batch([0.1, 0.2, 0.3]),
        overlay_image=_batch([0.05]),
        opacity=0.5,
        blend_mode="normal",
    )

    _assert_pair_values(
        blend_harness,
        [(0.1, 0.05), (0.2, 0.05), (0.3, 0.05)]
    )
    assert _output_values(response) == pytest.approx([0.15, 0.25, 0.35])


def test_single_base_broadcasts_across_ordered_overlay_batch(blend_harness) -> None:
    response = blend_harness.module.LF_Blend().on_exec(
        image=_batch([0.1]),
        overlay_image=_batch([0.01, 0.02, 0.03]),
        opacity=0.5,
        blend_mode="normal",
    )

    _assert_pair_values(
        blend_harness,
        [(0.1, 0.01), (0.1, 0.02), (0.1, 0.03)]
    )
    assert _output_values(response) == pytest.approx([0.11, 0.12, 0.13])


def test_incompatible_batch_cardinality_fails_before_processing(blend_harness) -> None:
    with pytest.raises(ValueError, match="same number of images"):
        blend_harness.module.LF_Blend().on_exec(
            image=_batch([0.1, 0.2]),
            overlay_image=_batch([0.01, 0.02, 0.03]),
            opacity=0.5,
            blend_mode="normal",
        )

    assert blend_harness.pairs == []
    assert blend_harness.sent == []
    assert not list(blend_harness.input_root.rglob("*.png"))


def test_history_dataset_uses_restart_stable_input_resources_without_widget(
    blend_harness,
) -> None:
    kwargs = {
        "image": _batch([0.1, 0.2]),
        "overlay_image": _batch([0.01, 0.02]),
        "opacity": 0.5,
        "blend_mode": "normal",
        "node_id": "blend-node",
    }

    blend_harness.module.LF_Blend().on_exec(**kwargs)
    event, payload, node_id = blend_harness.sent[0]
    first_dataset = payload["dataset"]

    assert (event, node_id) == ("blend", "blend-node")
    assert len(first_dataset["nodes"]) == 2
    resource_paths = []
    for history_node in first_dataset["nodes"]:
        assert set(history_node["cells"]) == {"lfImage", "lfImage_after"}
        for cell in history_node["cells"].values():
            url = cell["lfValue"]
            query = parse_qs(urlparse(url).query)
            assert query["type"] == ["input"]
            assert "nonce" not in query
            resource_path = blend_harness.input_root.joinpath(
                *query["subfolder"][0].split("/"),
                query["filename"][0],
            )
            assert resource_path.is_file()
            assert resource_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
            resource_paths.append(resource_path)

    first_mtimes = {path: path.stat().st_mtime_ns for path in resource_paths}
    blend_harness.module.LF_Blend().on_exec(**kwargs)
    second_dataset = blend_harness.sent[1][1]["dataset"]

    assert second_dataset == first_dataset
    assert {path: path.stat().st_mtime_ns for path in resource_paths} == first_mtimes
    assert len(set(resource_paths)) == 4
