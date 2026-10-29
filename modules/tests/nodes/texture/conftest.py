from __future__ import annotations

import pytest

from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    root = tmp_path / "input"
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(root))
    return root


@pytest.fixture
def events(monkeypatch):
    """Capture every node's live event instead of sending it."""
    sent = []
    from modules.nodes.texture import detail_transfer, edge_padding, masked_lab_grade, normal_map_repack
    for module in (detail_transfer, edge_padding, masked_lab_grade, normal_map_repack):
        monkeypatch.setattr(module, "safe_send_sync", lambda event, payload, node_id: sent.append(
            (event, payload, node_id)))
    return sent
