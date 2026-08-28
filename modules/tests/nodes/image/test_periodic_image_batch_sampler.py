from __future__ import annotations

import math
from types import SimpleNamespace

from PIL import Image
import pytest
import torch

from modules.nodes.image import periodic_image_batch_sampler as sampler_module


EXPECTED_124_TO_24 = [
    0,
    5,
    10,
    15,
    21,
    26,
    31,
    36,
    41,
    46,
    51,
    56,
    62,
    67,
    72,
    77,
    82,
    87,
    92,
    97,
    103,
    108,
    113,
    118,
]


@pytest.fixture
def preview_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path):
    saved_paths = []
    sent = []

    def cache_generated_preview(image):
        path = tmp_path / f"preview_{len(saved_paths)}.png"
        saved_paths.append(path)
        pixels = image[0].clamp(0, 1).mul(255).round().to(torch.uint8).numpy()
        Image.fromarray(pixels).save(path, format="PNG")
        return SimpleNamespace(
            url=f"/view?filename={path.name}&type=input&subfolder=preview",
        )

    monkeypatch.setattr(
        sampler_module, "cache_generated_preview", cache_generated_preview
    )
    monkeypatch.setattr(
        sampler_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    return {"saved_paths": saved_paths, "sent": sent}


def test_closed_124_frame_loop_selects_the_exact_24_frame_contract() -> None:
    source = (
        torch.arange(124, dtype=torch.float32)
        .reshape(124, 1, 1, 1)
        .expand(-1, -1, -1, 3)
    )

    sampled, receipt = sampler_module.sample_periodic_image_batch(
        source,
        target_count=24,
        loop_endpoint_policy="exclude_final_endpoint",
        source_fps=24.0,
        intended_fps=12.0,
    )

    assert receipt == {
        "schema": "lf.periodic_image_batch_sampler.receipt.v1",
        "sourceFrameCount": 124,
        "targetFrameCount": 24,
        "loopEndpointPolicy": "exclude_final_endpoint",
        "sourceFps": 24.0,
        "intendedFps": 12.0,
        "sourceEndpointSpanSeconds": 123 / 24,
        "sourcePlaybackDurationSeconds": 124 / 24,
        "intendedPlaybackDurationSeconds": 2.0,
        "indices": EXPECTED_124_TO_24,
    }
    assert sampled.shape == (24, 1, 1, 3)
    assert sampled[:, 0, 0, 0].tolist() == EXPECTED_124_TO_24
    assert 123 not in receipt["indices"]


def test_sampling_is_lossless_and_preserves_image_tensor_contract() -> None:
    source = torch.arange(10 * 3 * 4 * 4, dtype=torch.float64).reshape(10, 3, 4, 4)

    sampled, _receipt = sampler_module.sample_periodic_image_batch(
        source,
        target_count=4,
        loop_endpoint_policy="exclude_final_endpoint",
        source_fps=24,
        intended_fps=8,
    )
    indices = sampler_module.periodic_sample_indices(
        10,
        4,
        "exclude_final_endpoint",
    )

    assert sampled.dtype == source.dtype
    assert sampled.device == source.device
    assert sampled.shape == (4, 3, 4, 4)
    assert torch.equal(sampled, source[indices])


def test_include_final_endpoint_policy_keeps_both_source_endpoints() -> None:
    assert sampler_module.periodic_sample_indices(
        10, 4, "include_final_endpoint"
    ) == [
        0,
        3,
        6,
        9,
    ]
    assert sampler_module.periodic_sample_indices(
        10, 1, "include_final_endpoint"
    ) == [0]


@pytest.mark.parametrize(
    ("source_count", "target_count", "policy", "message"),
    [
        (0, 1, "include_final_endpoint", "source_count"),
        (1, 1, "exclude_final_endpoint", "at least two"),
        (4, 4, "exclude_final_endpoint", "before the final"),
        (4, 5, "include_final_endpoint", "cannot exceed source_count"),
        (4, 0, "include_final_endpoint", "target_count"),
        (4, True, "include_final_endpoint", "target_count"),
        (4, 1, "other", "loop_endpoint_policy"),
    ],
)
def test_index_planning_rejects_invalid_counts_and_policy(
    source_count: int,
    target_count: int,
    policy: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        sampler_module.periodic_sample_indices(source_count, target_count, policy)


@pytest.mark.parametrize(
    ("image", "message"),
    [
        (None, "torch.Tensor"),
        (torch.zeros((4, 8, 8)), "rank 4"),
        (torch.zeros((0, 8, 8, 3)), "at least one"),
        (torch.zeros((2, 0, 8, 3)), "positive height"),
        (torch.zeros((2, 8, 0, 3)), "positive height"),
        (torch.zeros((2, 8, 8, 0)), r"3 \(RGB\) or 4 \(RGBA\)"),
        (torch.zeros((2, 8, 8, 1)), r"3 \(RGB\) or 4 \(RGBA\)"),
    ],
)
def test_image_tensor_shape_is_validated(image, message: str) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        sampler_module.sample_periodic_image_batch(
            image,
            target_count=1,
            loop_endpoint_policy="include_final_endpoint",
            source_fps=24,
            intended_fps=12,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_fps", 0),
        ("source_fps", math.inf),
        ("source_fps", True),
        ("intended_fps", -1),
        ("intended_fps", math.nan),
        ("intended_fps", None),
    ],
)
def test_fps_metadata_must_be_positive_and_finite(field: str, value) -> None:
    kwargs = {
        "source_fps": 24,
        "intended_fps": 12,
    }
    kwargs[field] = value
    with pytest.raises(ValueError, match=field):
        sampler_module.sample_periodic_image_batch(
            torch.zeros((2, 8, 8, 3)),
            target_count=1,
            loop_endpoint_policy="include_final_endpoint",
            **kwargs,
        )


def test_node_publishes_ordered_masonry_history_without_requiring_widget(
    preview_runtime,
) -> None:
    source = torch.zeros((4, 3, 5, 4), dtype=torch.float32)
    source[..., 3] = 1.0
    for index in range(4):
        source[index, ..., 0] = index / 4

    response = sampler_module.LF_PeriodicImageBatchSampler().on_exec(
        image=source,
        target_count=4,
        loop_endpoint_policy="include_final_endpoint",
        source_fps=24,
        intended_fps=12,
        node_id=["sampler-17"],
    )

    sampled, receipt, image_list = response["result"]
    payload = response["ui"]["lf_output"][0]
    assert torch.equal(sampled, source)
    assert len(image_list) == 4
    assert torch.equal(torch.cat(image_list, dim=0), sampled)
    assert payload["receipt"] is receipt
    assert payload["preview"] == {
        "displayedOutputFrameIndices": [0, 1, 2, 3],
        "displayedFrameCount": 4,
        "totalOutputFrameCount": 4,
        "truncated": False,
    }
    assert [
        node["cells"]["lfImage"]["htmlProps"]["title"]
        for node in payload["dataset"]["nodes"]
    ] == ["Output frame 0", "Output frame 1", "Output frame 2", "Output frame 3"]
    assert preview_runtime["sent"] == [
        ("periodicimagebatchsampler", payload, "sampler-17")
    ]
    assert len(preview_runtime["saved_paths"]) == 4
    for path in preview_runtime["saved_paths"]:
        with Image.open(path) as preview:
            assert preview.mode == "RGBA"
            assert preview.size == (5, 3)


def test_masonry_preview_is_bounded_without_truncating_the_sampled_batch(
    preview_runtime,
) -> None:
    source = torch.rand((65, 2, 3, 3), dtype=torch.float32)

    response = sampler_module.LF_PeriodicImageBatchSampler().on_exec(
        image=source,
        target_count=65,
        loop_endpoint_policy="include_final_endpoint",
        source_fps=24,
        intended_fps=12,
    )

    sampled = response["result"][0]
    preview = response["ui"]["lf_output"][0]["preview"]
    assert torch.equal(sampled, source)
    assert preview["displayedFrameCount"] == 64
    assert preview["totalOutputFrameCount"] == 65
    assert preview["truncated"] is True
    assert preview["displayedOutputFrameIndices"][0] == 0
    assert preview["displayedOutputFrameIndices"][-1] == 64
    assert len(set(preview["displayedOutputFrameIndices"])) == 64
    assert len(preview_runtime["saved_paths"]) == 64
    with Image.open(preview_runtime["saved_paths"][0]) as image:
        assert image.mode == "RGB"


def test_public_node_schema_and_registration_are_generic() -> None:
    schema = sampler_module.LF_PeriodicImageBatchSampler.INPUT_TYPES()

    assert list(schema["required"]) == [
        "image",
        "target_count",
        "loop_endpoint_policy",
        "source_fps",
        "intended_fps",
    ]
    assert schema["required"]["loop_endpoint_policy"][0] == [
        "exclude_final_endpoint",
        "include_final_endpoint",
    ]
    assert schema["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert sampler_module.LF_PeriodicImageBatchSampler.OUTPUT_NODE is True
    assert sampler_module.LF_PeriodicImageBatchSampler.RETURN_TYPES == (
        "IMAGE",
        "JSON",
        "IMAGE",
    )
    assert sampler_module.LF_PeriodicImageBatchSampler.RETURN_NAMES == (
        "image",
        "receipt",
        "image_list",
    )
    assert sampler_module.LF_PeriodicImageBatchSampler.OUTPUT_IS_LIST == (
        False,
        False,
        True,
    )
    assert sampler_module.NODE_CLASS_MAPPINGS == {
        "LF_PeriodicImageBatchSampler": sampler_module.LF_PeriodicImageBatchSampler,
    }
    assert sampler_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_PeriodicImageBatchSampler": "Periodic image batch sampler",
    }
    public_contract = repr(schema).lower()
    assert "garage" not in public_contract
    assert "velora" not in public_contract
