from __future__ import annotations

import pytest
import torch

from modules.nodes.image import (
    resize_image_by_edge,
    resize_image_to_dimension,
    resize_image_to_square,
)


IMAGES = torch.zeros((3, 4, 5, 3), dtype=torch.float32)


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
