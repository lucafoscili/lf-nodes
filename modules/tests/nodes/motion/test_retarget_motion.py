"""Headless retarget-node orchestration; geometry has separate core tests."""
import json

import pytest

from modules.nodes.motion import retarget_motion as node_module


def test_public_schema_and_mapped_scalar_outputs():
    node = node_module.LF_RetargetMotion
    schema = node.INPUT_TYPES()
    assert list(schema["required"]) == ["motion_file", "body", "betas", "glb_path", "bone_map_path"]
    assert schema["required"]["body"][0] == ["female", "neutral", "male"]
    assert schema["required"]["body"][1]["default"] == "female"
    assert schema["required"]["betas"][1]["default"] == "0.5,-1.5"
    assert list(schema["optional"]) == ["keep_rest_facing", "flatten_slope", "ui_widget"]
    assert schema["optional"]["ui_widget"][0] == "LF_CODE"
    assert all(schema["optional"][name][1]["default"] == "[]" for name in ("keep_rest_facing", "flatten_slope"))
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert node.INPUT_IS_LIST is False
    assert node.OUTPUT_NODE is True
    assert node.FUNCTION == "on_exec"
    assert node.RETURN_TYPES == ("STRING", "JSON")
    assert node.RETURN_NAMES == ("glb_file", "report")
    assert node.OUTPUT_IS_LIST == (False, False)
    assert node_module.NODE_CLASS_MAPPINGS == {"LF_RetargetMotion": node}
    assert node_module.NODE_DISPLAY_NAME_MAPPINGS == {"LF_RetargetMotion": "Retarget motion"}


@pytest.mark.parametrize("node_id", [None, "retarget", ["retarget"]])
def test_headless_artifacts_and_shared_live_history(monkeypatch, tmp_path, node_id):
    output = tmp_path / "LF_Nodes" / "Motion" / "retarget_1.glb"
    output.parent.mkdir(parents=True)
    source = tmp_path / "source.glb"
    source.write_bytes(b"source stays intact")
    report = {"schema": "lf.retarget-motion.v1", "frames": 3, "unmapped_bones": ["helper"]}
    calls, sent = [], []
    monkeypatch.setattr(node_module, "resolve_body_model", lambda body: tmp_path / f"{body}.npz")
    monkeypatch.setattr(node_module.folder_paths, "get_output_directory", lambda: str(tmp_path))

    def resolve(**kwargs):
        assert kwargs == {"filename_prefix": "LF_Nodes/Motion/retarget", "base_output_path": str(tmp_path.resolve()),
                          "extension": "glb", "add_counter": True}
        return str(output), None, None

    def retarget(*args, **kwargs):
        calls.append((args, kwargs))
        return b"animated GLB", report

    monkeypatch.setattr(node_module, "resolve_filepath", resolve)
    monkeypatch.setattr(node_module, "retarget_motion", retarget)
    monkeypatch.setattr(node_module, "safe_send_sync", lambda *args: sent.append(args))
    response = node_module.LF_RetargetMotion().on_exec(
        "motion.json", "neutral", "0,1", str(source), "bones.json",
        keep_rest_facing='["left_foot"]', flatten_slope='["right_foot"]', node_id=node_id,
    )
    assert calls == [(("motion.json", tmp_path / "neutral.npz", "neutral", "0,1", str(source), "bones.json"),
                      {"keep_rest_facing": ("left_foot",), "flatten_slope": ("right_foot",)})]
    assert response["result"][0] == str(output)
    payload = response["ui"]["lf_output"][0]
    assert sent == [("retargetmotion", payload, node_id)]
    assert sent[0][1] is payload
    assert payload["json"] == response["result"][1] == {
        **report, "glb_file": "LF_Nodes/Motion/retarget_1.glb", "report_file": "LF_Nodes/Motion/retarget_1.json"}
    assert payload["file_names"] == ["LF_Nodes/Motion/retarget_1.glb", "LF_Nodes/Motion/retarget_1.json"]
    assert json.loads(payload["value"]) == payload["json"]
    assert json.loads(output.with_suffix(".json").read_text(encoding="utf-8")) == payload["json"]
    assert output.read_bytes() == b"animated GLB"
    assert source.read_bytes() == b"source stays intact"
    assert "glb_file" not in report


@pytest.mark.parametrize("name", ["keep_rest_facing", "flatten_slope"])
@pytest.mark.parametrize("value", ["invalid", "{}", '"pelvis"', '["ok", 1]', '[""]', None])
def test_invalid_policy_fails_before_model_or_writes(monkeypatch, name, value):
    def unexpected(*_args, **_kwargs):
        pytest.fail("Invalid policy must fail before resolving a model or writing files")
    monkeypatch.setattr(node_module, "resolve_body_model", unexpected)
    monkeypatch.setattr(node_module, "resolve_filepath", unexpected)
    with pytest.raises(ValueError, match=name):
        node_module.LF_RetargetMotion().on_exec("motion.json", **{name: value})


def test_failed_retarget_does_not_allocate_or_publish_outputs(monkeypatch):
    monkeypatch.setattr(node_module, "resolve_body_model", lambda _: "body.npz")
    def fail(*_args, **_kwargs):
        raise ValueError("Synthetic retarget failure")
    def unexpected(*_args, **_kwargs):
        pytest.fail("Failed retarget must not allocate outputs or publish UI")
    monkeypatch.setattr(node_module, "retarget_motion", fail)
    monkeypatch.setattr(node_module, "resolve_filepath", unexpected)
    monkeypatch.setattr(node_module, "safe_send_sync", unexpected)
    with pytest.raises(ValueError, match="Synthetic retarget failure"):
        node_module.LF_RetargetMotion().on_exec("motion.json")


def test_output_path_escape_is_rejected_before_artifact_write(monkeypatch, tmp_path):
    root = tmp_path / "output"
    root.mkdir()
    outside = tmp_path / "outside.glb"
    monkeypatch.setattr(node_module, "resolve_body_model", lambda _: "body.npz")
    monkeypatch.setattr(node_module, "retarget_motion", lambda *_a, **_k: (b"GLB", {}))
    monkeypatch.setattr(node_module.folder_paths, "get_output_directory", lambda: str(root))
    monkeypatch.setattr(node_module, "resolve_filepath", lambda **_: (str(outside), None, None))
    with pytest.raises(ValueError):
        node_module.LF_RetargetMotion().on_exec("motion.json")
    assert not outside.exists()
