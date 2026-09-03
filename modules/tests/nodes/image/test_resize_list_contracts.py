from __future__ import annotations

import pytest
import torch

from modules.nodes.image import (
    resize_image_by_edge,
    resize_image_to_dimension,
    resize_image_to_square,
)


IMAGES = torch.zeros((3, 4, 5, 3), dtype=torch.float32)


def test_resize_to_dimension_preserves_published_schema() -> None:
    schema = resize_image_to_dimension.LF_ResizeImageToDimension.INPUT_TYPES()

    assert tuple(schema["required"]) == (
        "image",
        "height",
        "width",
        "resize_method",
        "resize_mode",
        "pad_color",
    )
    assert tuple(schema["optional"]) == ("ui_widget",)
    assert tuple(schema["hidden"]) == ("node_id",)
    assert schema["required"]["height"][1]["default"] == 1216
    assert schema["required"]["width"][1]["default"] == 832
    assert schema["required"]["resize_method"][1]["default"] == "bicubic"
    assert schema["required"]["resize_mode"][1]["default"] == "crop"
    assert schema["required"]["pad_color"][1]["default"] == "000000"
    assert resize_image_to_dimension.LF_ResizeImageToDimension.INPUT_IS_LIST is True
    assert resize_image_to_dimension.LF_ResizeImageToDimension.RETURN_TYPES == (
        "IMAGE",
        "IMAGE",
        "INT",
    )
    assert resize_image_to_dimension.LF_ResizeImageToDimension.RETURN_NAMES == (
        "image",
        "image_list",
        "count",
    )
    assert resize_image_to_dimension.LF_ResizeImageToDimension.OUTPUT_IS_LIST == (
        False,
        True,
        False,
    )


@pytest.mark.parametrize("channels", [3, 4])
def test_resize_to_dimension_pad_color_uses_comfy_float_range_and_preserves_alpha(
    channels: int,
) -> None:
    image = torch.zeros((1, 2, 4, channels), dtype=torch.float32)
    image[..., :3] = torch.tensor((0.1, 0.2, 0.3), dtype=torch.float32)
    if channels == 4:
        image[..., 3] = 0.25

    response = resize_image_to_dimension.LF_ResizeImageToDimension().on_exec(
        image=[image],
        height=[4],
        width=[4],
        resize_method=["nearest exact"],
        resize_mode=["pad"],
        pad_color=["E6E6E6"],
    )
    output = response["result"][0]

    assert tuple(output.shape) == (1, 4, 4, channels)
    assert float(output.min()) >= 0.0
    assert float(output.max()) <= 1.0
    expected_fill = torch.full((3,), 230.0 / 255.0)
    assert torch.allclose(output[0, 0, 0, :3], expected_fill)
    assert torch.allclose(output[0, 1:3, :, :3], image[0, :, :, :3])
    if channels == 4:
        assert float(output[0, 0, 0, 3]) == 1.0
        assert torch.allclose(output[0, 1:3, :, 3], image[0, :, :, 3])


@pytest.mark.parametrize(
    ("node", "kwargs", "control_name"),
    [
        (
            resize_image_by_edge.LF_ResizeImageByEdge(),
            {
                "longest_edge": [True],
                "new_size": [64, 96],
                "resize_method": ["nearest-exact"],
            },
            "new_size",
        ),
        (
            resize_image_to_dimension.LF_ResizeImageToDimension(),
            {
                "height": [64, 96],
                "width": [64],
                "resize_method": ["nearest-exact"],
                "resize_mode": ["crop"],
                "pad_color": ["000000"],
            },
            "height",
        ),
        (
            resize_image_to_square.LF_ResizeImageToSquare(),
            {
                "square_size": [64, 96],
                "resize_method": ["nearest-exact"],
                "crop_position": ["center"],
            },
            "square_size",
        ),
    ],
)
def test_resize_nodes_reject_partial_parallel_controls(
    node,
    kwargs: dict,
    control_name: str,
) -> None:
    with pytest.raises(ValueError, match=control_name):
        node.on_exec(image=[IMAGES], **kwargs)


@pytest.mark.parametrize(
    ("module", "node", "function_name", "kwargs"),
    [
        (
            resize_image_by_edge,
            resize_image_by_edge.LF_ResizeImageByEdge(),
            "resize_image",
            {
                "longest_edge": [True],
                "new_size": [64],
                "resize_method": ["nearest-exact"],
            },
        ),
        (
            resize_image_to_dimension,
            resize_image_to_dimension.LF_ResizeImageToDimension(),
            "resize_and_crop_image",
            {
                "height": [64],
                "width": [64],
                "resize_method": ["nearest-exact"],
                "resize_mode": ["crop"],
                "pad_color": ["000000"],
            },
        ),
        (
            resize_image_to_square,
            resize_image_to_square.LF_ResizeImageToSquare(),
            "resize_to_square",
            {
                "square_size": [64],
                "resize_method": ["nearest-exact"],
                "crop_position": ["center"],
            },
        ),
    ],
)
def test_resize_nodes_publish_same_final_payload_to_history(
    monkeypatch,
    module,
    node,
    function_name: str,
    kwargs: dict,
) -> None:
    image = torch.zeros((1, 4, 5, 3), dtype=torch.float32)
    sent = []
    monkeypatch.setattr(module, function_name, lambda image, *_args: image)
    monkeypatch.setattr(module, "create_resize_node", lambda *_args: {"id": "resize"})
    monkeypatch.setattr(
        module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = node.on_exec(image=[image], node_id=["resize-node"], **kwargs)

    assert response["result"][2] == 1
    assert response["ui"]["lf_output"][0] is sent[0][1]
