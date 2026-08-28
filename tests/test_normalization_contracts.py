"""Focused behavior tests for tensor normalization helpers.

The source modules are loaded into a small synthetic package so these tests do
not execute the custom-node package root (and therefore do not require a live
ComfyUI installation).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
LOGIC_ROOT = ROOT / "modules" / "utils" / "helpers" / "logic"
PACKAGE_NAME = "_lf_normalization_contracts"


def _install_package(name: str, path: Path) -> types.ModuleType:
    package = types.ModuleType(name)
    package.__path__ = [str(path)]
    sys.modules[name] = package
    return package


def _load_source(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


_install_package(PACKAGE_NAME, LOGIC_ROOT)
normalize_output_image = _load_source(
    f"{PACKAGE_NAME}.normalize_output_image",
    LOGIC_ROOT / "normalize_output_image.py",
).normalize_output_image
_input_image_module = _load_source(
    f"{PACKAGE_NAME}.normalize_input_image",
    LOGIC_ROOT / "normalize_input_image.py",
)
normalize_input_image = _input_image_module.normalize_input_image
normalize_input_image_batches = _input_image_module.normalize_input_image_batches
normalize_output_mask = _load_source(
    f"{PACKAGE_NAME}.normalize_output_mask",
    LOGIC_ROOT / "normalize_output_mask.py",
).normalize_output_mask
normalize_masks_for_images = _load_source(
    f"{PACKAGE_NAME}.normalize_masks_for_images",
    LOGIC_ROOT / "normalize_masks_for_images.py",
).normalize_masks_for_images
_input_latent_module = _load_source(
    f"{PACKAGE_NAME}.normalize_input_latent",
    LOGIC_ROOT / "normalize_input_latent.py",
)
normalize_input_latent = _input_latent_module.normalize_input_latent
normalize_input_latent_batches = _input_latent_module.normalize_input_latent_batches
normalize_input_latent_list = _input_latent_module.normalize_input_latent_list
_output_latent_module = _load_source(
    f"{PACKAGE_NAME}.normalize_output_latent",
    LOGIC_ROOT / "normalize_output_latent.py",
)
normalize_output_latent = _output_latent_module.normalize_output_latent
normalize_output_latents = _output_latent_module.normalize_output_latents


def _image(
    value: float,
    *,
    height: int = 2,
    width: int = 3,
    channels: int = 3,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    return torch.full((1, height, width, channels), value, dtype=dtype)


def test_normalize_output_image_flattens_list_batches_in_input_order() -> None:
    first_batch = torch.cat((_image(1.0), _image(2.0)), dim=0)
    unbatched = _image(3.0)[0]
    second_batch = torch.cat((_image(4.0), _image(5.0)), dim=0)

    batch_list, image_list = normalize_output_image(
        [first_batch, unbatched, second_batch]
    )

    assert [tuple(image.shape) for image in image_list] == [(1, 2, 3, 3)] * 5
    assert [float(image[0, 0, 0, 0]) for image in image_list] == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
    ]
    assert len(batch_list) == 1
    assert tuple(batch_list[0].shape) == (5, 2, 3, 3)
    torch.testing.assert_close(batch_list[0], torch.cat(image_list, dim=0))


def test_batch_aware_image_input_preserves_coherent_batches() -> None:
    coherent = torch.cat((_image(1.0), _image(2.0)), dim=0)
    singleton = _image(3.0, height=4, width=5)

    batches = normalize_input_image_batches([[coherent], singleton])

    assert [tuple(batch.shape) for batch in batches] == [
        (2, 2, 3, 3),
        (1, 4, 5, 3),
    ]
    assert batches[0] is coherent


def test_normalize_output_image_groups_by_geometry_dtype_and_device() -> None:
    base_a = _image(1.0)
    different_height = _image(3.0, height=4)
    base_b = _image(2.0)
    different_width = _image(4.0, width=5)
    different_channels = _image(5.0, channels=4)
    different_dtype = _image(6.0, dtype=torch.float64)
    different_device = torch.empty((1, 2, 3, 3), device="meta")

    batch_list, image_list = normalize_output_image(
        [
            base_a,
            different_height,
            base_b,
            different_width,
            different_channels,
            different_dtype,
            different_device,
        ]
    )

    assert len(image_list) == 7
    assert [tuple(batch.shape) for batch in batch_list] == [
        (2, 2, 3, 3),
        (1, 4, 3, 3),
        (1, 2, 5, 3),
        (1, 2, 3, 4),
        (1, 2, 3, 3),
        (1, 2, 3, 3),
    ]
    assert [float(value) for value in batch_list[0][:, 0, 0, 0]] == [1.0, 2.0]
    assert batch_list[4].dtype == torch.float64
    assert batch_list[5].device.type == "meta"


@pytest.mark.parametrize(
    "invalid",
    [
        pytest.param(torch.zeros(2, 3), id="rank-2"),
        pytest.param(torch.zeros(1, 1, 2, 3, 4), id="rank-5"),
    ],
)
def test_normalize_output_image_rejects_unsupported_tensor_ranks(
    invalid: torch.Tensor,
) -> None:
    with pytest.raises(ValueError, match="must have shape"):
        normalize_output_image(invalid)


def test_normalize_output_image_rejects_empty_inputs() -> None:
    with pytest.raises(ValueError, match="empty"):
        normalize_output_image([])

    with pytest.raises(ValueError, match="at least one image"):
        normalize_output_image(torch.empty((0, 2, 3, 3)))


@pytest.mark.parametrize("channels", [1, 2, 5])
def test_image_normalizers_reject_non_rgb_channels(channels: int) -> None:
    invalid = torch.zeros((1, 2, 3, channels))

    with pytest.raises(ValueError, match="RGB or RGBA"):
        normalize_input_image(invalid)
    with pytest.raises(ValueError, match="RGB or RGBA"):
        normalize_output_image(invalid)


def test_normalize_input_image_rejects_an_empty_batch() -> None:
    with pytest.raises(ValueError, match="at least one image"):
        normalize_input_image(torch.empty((0, 2, 3, 3)))


@pytest.mark.parametrize("layout", ["hw", "bhw", "b1hw", "bhw1"])
def test_normalize_output_mask_accepts_each_supported_layout(layout: str) -> None:
    values = [2] if layout == "hw" else [2, 7]
    batch_hw = torch.stack(
        [torch.full((2, 3), value, dtype=torch.uint8) for value in values]
    )
    if layout == "hw":
        mask_input = batch_hw[0]
    elif layout == "bhw":
        mask_input = batch_hw
    elif layout == "b1hw":
        mask_input = batch_hw.unsqueeze(1)
    else:
        mask_input = batch_hw.unsqueeze(-1)

    batch_list, mask_list = normalize_output_mask(mask_input)

    assert [tuple(mask.shape) for mask in mask_list] == [(1, 2, 3)] * len(values)
    assert all(mask.dtype == torch.float32 for mask in mask_list)
    assert [float(mask[0, 0, 0]) for mask in mask_list] == values
    assert len(batch_list) == 1
    assert tuple(batch_list[0].shape) == (len(values), 2, 3)
    torch.testing.assert_close(batch_list[0], torch.cat(mask_list, dim=0))


def test_normalize_output_mask_rejects_multi_channel_4d_input() -> None:
    with pytest.raises(ValueError, match="singleton channel dimension"):
        normalize_output_mask(torch.zeros((2, 3, 4, 5)))


def test_normalize_output_mask_rejects_dual_singleton_layout_ambiguity() -> None:
    with pytest.raises(ValueError, match="ambiguous"):
        normalize_output_mask(torch.zeros((2, 1, 5, 1)))


def test_normalize_output_mask_groups_by_geometry_and_device() -> None:
    cpu_a = torch.ones((1, 2, 3))
    cpu_b = torch.zeros((1, 2, 3))
    different_geometry = torch.ones((1, 4, 3))
    different_device = torch.empty((1, 2, 3), device="meta")

    batch_list, mask_list = normalize_output_mask(
        [cpu_a, different_geometry, cpu_b, different_device]
    )

    assert len(mask_list) == 4
    assert [tuple(batch.shape) for batch in batch_list] == [
        (2, 2, 3),
        (1, 4, 3),
        (1, 2, 3),
    ]
    assert batch_list[-1].device.type == "meta"


def test_normalize_masks_for_images_flattens_a_wrapped_batch() -> None:
    batched_mask = torch.stack(
        [torch.full((2, 3), value) for value in (1.0, 2.0, 3.0)]
    )

    masks = normalize_masks_for_images([batched_mask], image_count=3)

    assert len(masks) == 3
    assert [tuple(mask.shape) for mask in masks] == [(1, 2, 3)] * 3
    assert [float(mask[0, 0, 0]) for mask in masks] == [1.0, 2.0, 3.0]


def test_normalize_masks_for_images_allows_only_singleton_or_exact_cardinality() -> None:
    masks = [torch.full((2, 3), value) for value in (1.0, 2.0, 3.0)]

    singleton = normalize_masks_for_images(masks[0], image_count=3)
    exact = normalize_masks_for_images(masks, image_count=3)

    assert len(singleton) == 1
    assert len(exact) == 3
    with pytest.raises(ValueError, match="Mask count mismatch"):
        normalize_masks_for_images(masks[:2], image_count=3)


@pytest.mark.parametrize(
    ("latent", "error", "message"),
    [
        pytest.param({}, KeyError, "must include a 'samples' tensor", id="missing"),
        pytest.param(
            {"samples": "not-a-tensor"},
            TypeError,
            "must be a torch.Tensor",
            id="non-tensor",
        ),
        pytest.param(
            {"samples": torch.zeros((4, 2, 2))},
            ValueError,
            "must have shape",
            id="rank-3",
        ),
        pytest.param(
            {"samples": torch.empty((0, 4, 2, 2))},
            ValueError,
            "non-empty batch",
            id="empty-batch",
        ),
    ],
)
def test_normalize_input_latent_validates_a_single_entry(
    latent: dict,
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error, match=message):
        normalize_input_latent(latent)


@pytest.mark.parametrize(
    "batch_index",
    [
        pytest.param([11, 22, 33], id="list"),
        pytest.param((11, 22, 33), id="tuple"),
        pytest.param(torch.tensor([11, 22, 33]), id="tensor"),
    ],
)
def test_normalize_output_latent_slices_samples_and_metadata_per_item(
    batch_index,
) -> None:
    samples = torch.stack(
        [torch.full((4, 2, 2), value) for value in (1.0, 2.0, 3.0)]
    )
    noise_mask = torch.stack(
        [torch.full((1, 2, 2), value) for value in (4.0, 5.0, 6.0)]
    )
    latent = {
        "samples": samples,
        "noise_mask": noise_mask,
        "batch_index": batch_index,
        "custom": {"name": "kept"},
    }

    latent_batch, latent_list = normalize_output_latent(latent)

    assert latent_batch is not latent
    assert latent_batch["samples"] is samples
    assert latent_batch["noise_mask"] is noise_mask
    assert latent_batch["custom"] is not latent["custom"]
    torch.testing.assert_close(latent_batch["samples"], samples)
    assert len(latent_list) == 3
    assert [tuple(item["samples"].shape) for item in latent_list] == [
        (1, 4, 2, 2)
    ] * 3
    assert [float(item["samples"][0, 0, 0, 0]) for item in latent_list] == [
        1.0,
        2.0,
        3.0,
    ]
    assert [tuple(item["noise_mask"].shape) for item in latent_list] == [
        (1, 1, 2, 2)
    ] * 3
    assert [float(item["noise_mask"][0, 0, 0, 0]) for item in latent_list] == [
        4.0,
        5.0,
        6.0,
    ]
    for item, expected in zip(latent_list, (11, 22, 33)):
        sliced_index = item["batch_index"]
        if isinstance(batch_index, torch.Tensor):
            torch.testing.assert_close(sliced_index, torch.tensor([expected]))
        else:
            assert isinstance(sliced_index, type(batch_index))
            assert list(sliced_index) == [expected]
        assert item["custom"] == {"name": "kept"}
        assert item["custom"] is not latent["custom"]
        assert item["samples"].untyped_storage().data_ptr() == samples.untyped_storage().data_ptr()


def test_latent_list_seam_preserves_mixed_shapes_and_primary_compatibility_group() -> None:
    first = {"samples": torch.full((1, 4, 3, 5), 0.2)}
    second = {"samples": torch.full((1, 4, 2, 7), 0.7)}
    third = {"samples": torch.full((1, 4, 3, 5), 0.9)}

    primary_batch, latent_list = normalize_output_latents(
        [first, [second, third]]
    )

    assert primary_batch["samples"].shape == (2, 4, 3, 5)
    assert [tuple(item["samples"].shape) for item in latent_list] == [
        (1, 4, 3, 5),
        (1, 4, 2, 7),
        (1, 4, 3, 5),
    ]
    assert [float(item["samples"][0, 0, 0, 0]) for item in latent_list] == pytest.approx([
        0.2,
        0.7,
        0.9,
    ])
    flattened = normalize_input_latent_list([[first], second])
    assert [tuple(item["samples"].shape) for item in flattened] == [
        (1, 4, 3, 5),
        (1, 4, 2, 7),
    ]


def test_batch_aware_latent_input_preserves_coherent_batches() -> None:
    coherent = {
        "samples": torch.zeros((2, 4, 3, 5)),
        "batch_index": [10, 11],
    }
    singleton = {"samples": torch.ones((1, 4, 2, 7))}

    batches = normalize_input_latent_batches([[coherent], singleton])

    assert [tuple(item["samples"].shape) for item in batches] == [
        (2, 4, 3, 5),
        (1, 4, 2, 7),
    ]
    assert batches[0]["samples"] is coherent["samples"]
    assert batches[0]["batch_index"] == [10, 11]


def test_single_input_latent_keeps_tensor_storage_and_copies_mutable_metadata() -> None:
    samples = torch.ones((1, 4, 2, 2))
    custom_tensor = torch.arange(3)
    custom = {"label": ["source"]}
    source = {
        "samples": samples,
        "custom_tensor": custom_tensor,
        "custom": custom,
    }

    normalized = normalize_input_latent(source)

    assert normalized is not source
    assert normalized["samples"] is samples
    assert normalized["custom_tensor"] is custom_tensor
    assert normalized["custom"] == custom
    assert normalized["custom"] is not custom


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        ({"noise_mask": torch.zeros((2, 1, 2, 2))}, "noise_mask"),
        ({"batch_index": [1, 2]}, "batch_index"),
        ({"batch_index": torch.tensor([1, 2])}, "batch_index"),
    ],
)
def test_single_input_latent_rejects_misaligned_batch_metadata(
    metadata: dict,
    message: str,
) -> None:
    latent = {"samples": torch.zeros((3, 4, 2, 2)), **metadata}

    with pytest.raises(ValueError, match=message):
        normalize_input_latent(latent)


@pytest.mark.parametrize("metadata_key", ["noise_mask", "batch_index"])
def test_input_latent_rejects_partial_batch_coupled_metadata(
    metadata_key: str,
) -> None:
    first = {
        "samples": torch.zeros((1, 4, 2, 2)),
        "noise_mask": torch.ones((1, 1, 2, 2)),
        "batch_index": [3],
    }
    first = {"samples": first["samples"], metadata_key: first[metadata_key]}
    second = {"samples": torch.ones((1, 4, 2, 2))}

    with pytest.raises(ValueError, match=f"Latent {metadata_key} must be present"):
        normalize_input_latent([first, second])


def test_input_latent_rejects_mixed_batch_index_representations() -> None:
    first = {
        "samples": torch.zeros((1, 4, 2, 2)),
        "batch_index": torch.tensor([3]),
    }
    second = {
        "samples": torch.ones((1, 4, 2, 2)),
        "batch_index": [4],
    }

    with pytest.raises(TypeError, match="one representation"):
        normalize_input_latent([first, second])


def test_input_latent_broadcasts_singleton_batch_metadata_per_entry() -> None:
    first = {
        "samples": torch.zeros((2, 4, 2, 2)),
        "noise_mask": torch.ones((1, 1, 2, 2)),
        "batch_index": [7],
    }
    second = {
        "samples": torch.ones((1, 4, 2, 2)),
        "noise_mask": torch.zeros((1, 1, 2, 2)),
        "batch_index": [9],
    }

    normalized = normalize_input_latent([first, second])

    assert normalized["noise_mask"].shape == (3, 1, 2, 2)
    assert normalized["batch_index"] == [7, 7, 9]


@pytest.mark.parametrize(
    ("metadata", "message"),
    [
        pytest.param(
            {"noise_mask": torch.zeros((2, 1, 2, 2))},
            "noise_mask",
            id="noise-mask",
        ),
        pytest.param(
            {"batch_index": [4, 5]},
            "batch_index",
            id="batch-index-list",
        ),
        pytest.param(
            {"batch_index": torch.tensor([4, 5])},
            "batch_index",
            id="batch-index-tensor",
        ),
    ],
)
def test_normalize_output_latent_rejects_mismatched_metadata_cardinality(
    metadata: dict,
    message: str,
) -> None:
    latent = {"samples": torch.zeros((3, 4, 2, 2)), **metadata}

    with pytest.raises(ValueError, match=message):
        normalize_output_latent(latent)
