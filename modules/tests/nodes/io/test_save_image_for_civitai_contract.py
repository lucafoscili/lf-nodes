from __future__ import annotations

import pytest
import torch

from modules.nodes.io import save_image_for_civitai


def test_save_image_rejects_partial_prefix_cardinality_before_writing(
    monkeypatch,
) -> None:
    writes = []
    monkeypatch.setattr(
        save_image_for_civitai,
        "resolve_filepath",
        lambda *_args, **_kwargs: writes.append(True),
    )

    with pytest.raises(
        ValueError,
        match="filename_prefix.*exactly 3 values; got 2",
    ):
        save_image_for_civitai.LF_SaveImageForCivitAI().on_exec(
            image=torch.zeros((3, 2, 2, 3), dtype=torch.float32),
            filename_prefix=["first", "second"],
            add_timestamp=[False],
            embed_workflow=[False],
            extension=["png"],
            quality=[100],
        )

    assert writes == []


@pytest.mark.parametrize(
    ("prefixes", "expected"),
    [
        (["shared"], ["shared", "shared"]),
        (["first", "second"], ["first", "second"]),
    ],
)
def test_save_image_routes_prefixes_and_publishes_durable_outputs(
    monkeypatch,
    tmp_path,
    prefixes: list[str],
    expected: list[str],
) -> None:
    calls = []
    sent = []

    def resolve_filepath(*, filename_prefix, **_kwargs):
        index = len(calls)
        calls.append(filename_prefix)
        filename = f"{filename_prefix}-{index}.png"
        return str(tmp_path / filename), "", filename

    monkeypatch.setattr(save_image_for_civitai, "resolve_filepath", resolve_filepath)
    monkeypatch.setattr(
        save_image_for_civitai,
        "get_comfy_dir",
        lambda _kind: str(tmp_path),
    )
    monkeypatch.setattr(
        save_image_for_civitai,
        "get_resource_url",
        lambda _subfolder, filename, _kind: f"/view/{filename}",
    )
    monkeypatch.setattr(
        save_image_for_civitai,
        "create_masonry_node",
        lambda filename, url, index: {"id": index, "filename": filename, "url": url},
    )
    monkeypatch.setattr(
        save_image_for_civitai,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    response = save_image_for_civitai.LF_SaveImageForCivitAI().on_exec(
        image=torch.zeros((2, 2, 2, 3), dtype=torch.float32),
        filename_prefix=prefixes,
        add_timestamp=[False],
        embed_workflow=[False],
        extension=["png"],
        quality=[100],
        civitai_metadata=["metadata"],
        prompt=[{"workflow": "kept"}],
        extra_pnginfo=[{"extra": "kept"}],
        node_id=[["save-node"]],
    )

    file_names, metadata = response["result"]
    assert calls == expected
    assert isinstance(file_names, list) and len(file_names) == 2
    assert metadata == "metadata"
    assert all((tmp_path / filename).is_file() for filename in file_names)
    assert response["ui"]["images"] == [
        {"filename": filename, "subfolder": "", "type": "output"}
        for filename in file_names
    ]
    final_payload = response["ui"]["lf_output"][0]
    assert final_payload["file_names"] == file_names
    assert sent == [("saveimageforcivitai", final_payload, [["save-node"]])]
