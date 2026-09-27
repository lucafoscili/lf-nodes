import ast
import hashlib
from pathlib import Path

import pytest
from PIL import Image

from modules.nodes.io import load_images


def test_published_schema_is_unchanged():
    node = load_images.LF_LoadImages
    tree = ast.parse(Path(load_images.__file__).read_text())
    cls = next(item for item in tree.body if isinstance(item, ast.ClassDef))
    inputs = next(item for item in cls.body if isinstance(item, ast.FunctionDef) and item.name == "INPUT_TYPES")
    assert hashlib.sha256(ast.dump(inputs, include_attributes=False).encode()).hexdigest() == "4f1c8a538ac82fd157b2f72c5fb6f8933c5d0423443127b49db0c6f19d9a2a74"
    assert node.RETURN_NAMES == ("image", "image_list", "name", "creation_date", "nr", "selected_image", "selected_index", "selected_name", "metadata")
    assert node.RETURN_TYPES == ("IMAGE", "IMAGE", "STRING", "STRING", "INT", "IMAGE", "INT", "STRING", "JSON")
    assert node.OUTPUT_IS_LIST == (False, True, True, True, False, False, False, False, False)


def test_file_identity_wins_over_stale_index_in_fresh_and_cached_listing(tmp_path, monkeypatch):
    Image.new("RGB", (2, 2), "red").save(tmp_path / "first.png")
    Image.new("RGB", (2, 2), "blue").save(tmp_path / "wanted.png")
    monkeypatch.setattr(load_images, "resolve_input_directory_path", lambda _: (str(tmp_path), "", False))
    monkeypatch.setattr(load_images, "get_comfy_dir", lambda _: str(tmp_path))
    monkeypatch.setattr(load_images.os, "walk", lambda _: [(str(tmp_path), [], ["first.png", "wanted.png"])])
    events = []
    monkeypatch.setattr(load_images, "safe_send_sync", lambda *args: events.append(args))
    node = load_images.LF_LoadImages()
    controls = dict(dir=str(tmp_path), subdir=False, strip_ext=True, load_cap=0, dummy_output=False, cache_images=True, copy_into_input_dir=False)
    identity = {"directory": str(tmp_path), "relative_path": "wanted.png"}
    for _ in range(2):
        result = node.on_exec(**controls, ui_widget={"index": 0, "file_identity": identity})
        assert result[6:8] == (1, "wanted")
        assert result[5][0, 0, 0].tolist() == [0.0, 0.0, 1.0]
        assert events[-1][1]["dataset"]["nodes"][1]["cells"]["lfImage"]["file_identity"] == identity
    assert node.on_exec(**controls, ui_widget={"index": 0})[7] == "first"
    assert node.on_exec(**controls, ui_widget={"name": "wanted"})[7] == "wanted"
    for invalid in (
        {"directory": str(tmp_path), "relative_path": "missing.png"},
        {"directory": str(tmp_path / "other"), "relative_path": "wanted.png"},
    ):
        with pytest.raises(ValueError, match="Selected image"):
            node.on_exec(**controls, ui_widget={"index": 0, "file_identity": invalid})
