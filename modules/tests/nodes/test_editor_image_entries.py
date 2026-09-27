import ast
import copy
import hashlib
from pathlib import Path

import pytest
from PIL import Image

from modules.nodes.image import images_editing_breakpoint as breakpoint
from modules.utils.helpers.editing.dataset import (
    apply_editor_config_to_dataset,
    build_editor_config_from_dataset,
    normalize_editor_image_entries,
)
from modules.utils.helpers.editing.sessions import session as sessions


ENTRIES = [{"id": "one", "label": "First panel"}, {"id": "two", "label": "Second panel"}]


def test_breakpoint_published_schema_unchanged():
    tree = ast.parse(Path(breakpoint.__file__).read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    inputs = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "INPUT_TYPES")
    assert hashlib.sha256(ast.dump(inputs, include_attributes=False).encode()).hexdigest() == "8db91a23ee00a4ea2eeef7493f37dcf09890936997a8d012d21de4f5aa4cf3cb"
    node = breakpoint.LF_ImagesEditingBreakpoint
    assert node.RETURN_TYPES == ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "JSON")
    assert node.RETURN_NAMES == ("image", "image_list", "orig_image", "orig_image_list", "config")
    assert node.OUTPUT_IS_LIST == (False, True, False, True, False)


@pytest.mark.parametrize("entries", [[], ENTRIES[:1], [ENTRIES[0], ENTRIES[0]], [{"id": "", "label": "x"}, ENTRIES[1]], None])
def test_invalid_entries_fail(entries):
    with pytest.raises(ValueError, match="image_entries"):
        normalize_editor_image_entries(entries, 2)


def test_labels_order_snapshot_identity_and_legacy_collection(tmp_path, monkeypatch):
    for name, color in [("red.png", (255, 0, 0, 64)), ("blue.png", (0, 0, 255, 128)), ("edited.png", (0, 255, 0, 64))]:
        Image.new("RGBA", (2, 2), color).save(tmp_path / name)
    monkeypatch.setattr(sessions, "get_comfy_dir", lambda _: str(tmp_path))
    dataset = {"context_id": str(tmp_path / "session.json"), "nodes": [
        {"id": str(index), "cells": {"lfImage": {"value": f"/view?filename={name}&type=temp", "htmlProps": {"id": name}}}}
        for index, name in enumerate(["red.png", "blue.png"])
    ]}
    config = {"image_entries": copy.deepcopy(ENTRIES), "defaults": {"brush": {"size": 20}}}
    apply_editor_config_to_dataset(dataset, config)
    assert build_editor_config_from_dataset(dataset)["image_entries"] == ENTRIES
    assert dataset["nodes"][0]["cells"]["lfImage"]["htmlProps"]["title"] == "First panel"
    captioned_cell = dataset["nodes"][0]["cells"]["lfImage"]
    assert "content: attr(title)" in captioned_cell["lfStyle"]
    assert "pointer-events: none" in captioned_cell["lfStyle"]
    assert "First panel" not in captioned_cell["lfStyle"]
    assert captioned_cell["lfHtmlAttributes"]["alt"] == "First panel"
    session = sessions.EditingSession("entry-test")
    session.bind_dataset_context(dataset, default_status="pending")
    session.register_context(dataset)
    # Save snapshot updates only the existing cell URLs, preserving node identity.
    cell = dataset["nodes"][0]["cells"]["lfImage"]
    cell["value"] = cell["lfValue"] = "/view?filename=edited.png&type=temp"
    dataset["nodes"].reverse()
    result = session.collect_results(dataset)
    assert result.image_list[0][0, 0, 0, :3].tolist() == [0, 1, 0]
    assert result.image_list[1][0, 0, 0, :3].tolist() == [0, 0, 1]
    assert result.image_list[0].shape == (1, 2, 2, 4)
    assert float(result.image_list[0][0, 0, 0, 3]) == pytest.approx(64 / 255)
    assert sessions.EditingSession("legacy").collect_results(dataset).image_list[0][0, 0, 0, :3].tolist() == [0, 0, 1]
    for nodes, message in [
        (dataset["nodes"][:1], "deleted"),
        ([dataset["nodes"][0]] * 2, "duplicate"),
        ([{"id": "unexpected"}], "unexpected"),
    ]:
        with pytest.raises(ValueError, match=message):
            session.collect_results({**dataset, "nodes": nodes})
    session.cleanup(dataset)
