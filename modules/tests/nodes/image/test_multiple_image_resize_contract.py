from __future__ import annotations

import torch

from modules.nodes.image import multiple_image_resize_for_web


def test_multiple_resize_returns_scalar_name_list_companion_and_history(
    monkeypatch,
) -> None:
    sent = []
    monkeypatch.setattr(
        multiple_image_resize_for_web.Image.Image,
        "resize",
        lambda self, *_args, **_kwargs: self.copy(),
    )
    monkeypatch.setattr(
        multiple_image_resize_for_web,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = multiple_image_resize_for_web.LF_MultipleImageResizeForWeb().on_exec(
        image=[torch.zeros((1, 2, 3, 3), dtype=torch.float32)],
        file_name=["sample.png"],
        node_id=["resize-web"],
    )
    result = response["result"]

    assert isinstance(result[2], str)
    assert result[2] == "sample"
    assert isinstance(result[3], list)
    assert result[3][0] == "sample"
    assert len(result[1]) == len(result[3]) == 9
    assert response["ui"]["lf_output"][0] is sent[0][1]


def test_multiple_resize_rejects_filename_mismatch() -> None:
    node = multiple_image_resize_for_web.LF_MultipleImageResizeForWeb()

    try:
        node.on_exec(
            image=[torch.zeros((2, 2, 3, 3), dtype=torch.float32)],
            file_name=["only-one.png"],
        )
    except ValueError as error:
        assert "exactly one name" in str(error)
    else:
        raise AssertionError("filename mismatch should fail before resizing")
