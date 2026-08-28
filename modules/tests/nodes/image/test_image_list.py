from __future__ import annotations

import torch
import pytest

from modules.nodes.image import image_list as image_list_module
from modules.utils.helpers.ui import create_masonry_node


@pytest.fixture(autouse=True)
def preview_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path):
    cached_images = []
    sent = []

    def create_cached_masonry(image, *, index, label):
        cached_images.append(image.clone())
        return create_masonry_node(
            label,
            f"/view?filename=image-{index}.png&type=input",
            index,
        )

    monkeypatch.setattr(
        image_list_module,
        "create_cached_masonry_node",
        create_cached_masonry,
    )
    monkeypatch.setattr(
        image_list_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )
    return {"cached_images": cached_images, "sent": sent}


def test_collects_mixed_dimensions_and_channels_without_resizing() -> None:
    first = torch.rand((1, 40, 80, 3), dtype=torch.float32)
    second = torch.rand((1, 72, 31, 4), dtype=torch.float32)

    response = image_list_module.LF_ImageList().on_exec(
        image_1=[first],
        image_2=[second],
    )
    images = response["result"][0]

    assert [tuple(image.shape) for image in images] == [
        (1, 40, 80, 3),
        (1, 72, 31, 4),
    ]
    assert torch.equal(images[0], first)
    assert torch.equal(images[1], second)


def test_flattens_each_batch_in_input_then_preserves_input_order() -> None:
    batch = torch.stack(
        (
            torch.full((20, 30, 3), 0.1),
            torch.full((20, 30, 3), 0.2),
        )
    )
    final = torch.full((1, 9, 7, 3), 0.3)

    response = image_list_module.LF_ImageList().on_exec(
        image_1=[batch],
        image_3=[final],
    )
    images = response["result"][0]

    assert len(images) == 3
    assert [float(image[0, 0, 0, 0]) for image in images] == pytest.approx([
        0.1,
        0.2,
        0.3,
    ])
    assert [tuple(image.shape) for image in images] == [
        (1, 20, 30, 3),
        (1, 20, 30, 3),
        (1, 9, 7, 3),
    ]


def test_publishes_live_and_durable_preview_without_requiring_widget(
    preview_runtime,
) -> None:
    first = torch.full((1, 5, 7, 3), 0.25)
    second = torch.full((1, 3, 4, 4), 0.75)

    response = image_list_module.LF_ImageList().on_exec(
        image_1=[first],
        image_2=[second],
        node_id=["node-17"],
    )

    images = response["result"][0]
    dataset = response["ui"]["lf_output"][0]["dataset"]
    assert [tuple(image.shape) for image in images] == [
        (1, 5, 7, 3),
        (1, 3, 4, 4),
    ]
    assert [node["id"] for node in dataset["nodes"]] == ["1", "2"]
    assert all(
        node["cells"]["lfImage"]["lfValue"].startswith("/view?")
        for node in dataset["nodes"]
    )
    assert preview_runtime["sent"] == [
        ("imagelist", {"dataset": dataset}, "node-17")
    ]

    cached_images = preview_runtime["cached_images"]
    assert len(cached_images) == 2
    assert [tuple(image.shape) for image in cached_images] == [
        (1, 5, 7, 3),
        (1, 3, 4, 4),
    ]
    assert torch.equal(cached_images[0], first)
    assert torch.equal(cached_images[1], second)


def test_schema_is_headless_and_mapping_is_generic() -> None:
    schema = image_list_module.LF_ImageList.INPUT_TYPES()

    assert list(schema["required"]) == ["image_1"]
    assert list(schema["optional"]) == [
        f"image_{index}" for index in range(2, 17)
    ] + ["ui_widget"]
    assert schema["optional"]["ui_widget"][0] == "LF_MASONRY"
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert image_list_module.LF_ImageList.INPUT_IS_LIST is True
    assert image_list_module.LF_ImageList.OUTPUT_IS_LIST == (True,)
    assert image_list_module.LF_ImageList.OUTPUT_NODE is True
    assert image_list_module.LF_ImageList.RETURN_TYPES == ("IMAGE",)
    assert image_list_module.NODE_CLASS_MAPPINGS == {
        "LF_ImageList": image_list_module.LF_ImageList
    }
    assert image_list_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_ImageList": "Images to list"
    }
