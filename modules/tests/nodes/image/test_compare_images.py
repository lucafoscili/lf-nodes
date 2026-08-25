from __future__ import annotations

from PIL import Image
import pytest
import torch

from modules.nodes.image import compare_images as compare_module


def test_compare_images_publishes_history_dataset_and_preserves_rgba(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    node = compare_module.LF_CompareImages()
    monkeypatch.setattr(node._temp_cache, "cleanup", lambda: None)

    def resolve_filepath(*, filename_prefix, image, temp_cache):
        del image, temp_cache
        path = tmp_path / f"{filename_prefix}.png"
        return path, "", path.name

    sent = []
    monkeypatch.setattr(compare_module, "resolve_filepath", resolve_filepath)
    monkeypatch.setattr(
        compare_module,
        "get_resource_url",
        lambda subfolder, filename, storage_type: (
            f"/view?filename={filename}&type={storage_type}&subfolder={subfolder}"
        ),
    )
    monkeypatch.setattr(
        compare_module,
        "safe_send_sync",
        lambda event, payload, node_id: sent.append((event, payload, node_id)),
    )

    before = torch.rand(1, 7, 5, 4)
    after = torch.rand(1, 12, 9, 4)
    response = node.on_exec(
        image_before=before,
        image_after=after,
        node_id="compare-node",
    )

    dataset = response["ui"]["lf_output"][0]["dataset"]
    assert response["result"][3] is dataset
    assert len(dataset["nodes"]) == 1
    assert dataset["nodes"][0]["cells"]["lfImage"]["lfValue"].startswith("/view?")
    assert dataset["nodes"][0]["cells"]["lfImage_after"]["lfValue"].startswith(
        "/view?"
    )
    assert sent == [("compareimages", {"dataset": dataset}, "compare-node")]

    with Image.open(tmp_path / "compare_before.png") as saved_before:
        assert saved_before.mode == "RGBA"
    with Image.open(tmp_path / "compare_after.png") as saved_after:
        assert saved_after.mode == "RGBA"


def test_compare_images_rejects_mismatched_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    node = compare_module.LF_CompareImages()
    monkeypatch.setattr(node._temp_cache, "cleanup", lambda: None)

    with pytest.raises(ValueError, match="same length"):
        node.on_exec(
            image_before=torch.rand(2, 8, 8, 3),
            image_after=torch.rand(1, 8, 8, 3),
        )
