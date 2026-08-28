from __future__ import annotations

import torch

from modules.nodes.io import load_metadata
from modules.utils.constants import Input


def test_load_metadata_returns_first_item_full_list_and_durable_payload(
    monkeypatch,
) -> None:
    monkeypatch.setattr(load_metadata, "safe_send_sync", lambda *_args: None)
    monkeypatch.setattr(
        load_metadata,
        "extract_jpeg_metadata",
        lambda _image, file_name: {"source": file_name},
    )
    image = torch.stack(
        (
            torch.zeros((2, 3, 3), dtype=torch.float32),
            torch.ones((2, 3, 3), dtype=torch.float32),
        )
    )

    response = load_metadata.LF_LoadMetadata().on_exec(
        image=image,
        node_id="metadata-node",
    )

    expected = [
        {
            "file": "input_image_0",
            "metadata": {"source": "input_image_0"},
        },
        {
            "file": "input_image_1",
            "metadata": {"source": "input_image_1"},
        },
    ]
    node = load_metadata.LF_LoadMetadata
    assert node.RETURN_TYPES == (Input.JSON, Input.JSON)
    assert node.RETURN_NAMES == ("metadata", "metadata_list")
    assert node.OUTPUT_IS_LIST == (False, True)
    assert response == {
        "ui": {"lf_output": [{"metadata": expected}]},
        "result": (expected[0], expected),
    }
    assert isinstance(response["result"][0], dict)
    assert isinstance(response["result"][1], list)


def test_load_metadata_uses_empty_object_as_the_singular_default(
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.setattr(load_metadata, "safe_send_sync", lambda *_args: None)
    monkeypatch.setattr(load_metadata, "get_comfy_dir", lambda _kind: str(tmp_path))

    response = load_metadata.LF_LoadMetadata().on_exec(
        file_names="",
        upload_dir="temp",
    )

    assert response == {
        "ui": {"lf_output": [{"metadata": []}]},
        "result": ({}, []),
    }
