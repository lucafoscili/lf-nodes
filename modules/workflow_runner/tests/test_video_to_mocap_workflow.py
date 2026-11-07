"""Offline graph, upload and control contracts for video-to-mocap."""

from pathlib import Path

import pytest

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import _WORKFLOW_MODULES
from modules.workflow_runner.workflows import video_to_mocap as workflow_module


WORKFLOW = workflow_module.WORKFLOW


def test_block_is_registered_and_exposes_upload_and_result_cards():
    assert "video_to_mocap" in _WORKFLOW_MODULES
    assert WORKFLOW.category == "Motion"
    assert WORKFLOW.inputs[0].id == "video_path"
    assert WORKFLOW.inputs[0].shape == "upload"
    assert WORKFLOW.inputs[0].props["lfHtmlAttributes"]["accept"] == "video/*"
    assert [(cell.node_id, cell.shape) for cell in WORKFLOW.outputs] == [
        ("render_motion", "code"), ("extract_motion", "code"),
    ]
    cells = {cell.id: cell for cell in WORKFLOW.inputs}
    assert cells["engine"].shape == "select"
    assert cells["engine"].props["lfValue"] == "ExMR"
    assert cells["engine"].props["lfDataset"]["nodes"] == [
        {"id": "ExMR", "value": "ExMR", "workflowValue": "ExMR"},
    ]
    assert cells["include_shape"].shape == "toggle"
    assert cells["include_shape"].props["lfValue"] is False
    assert cells["motion_correction"].shape == "toggle"
    assert cells["motion_correction"].props["lfValue"] is True
    assert cells["stage_timeout_seconds"].props["lfValue"] == "0"
    assert cells["stage_timeout_seconds"].props["lfHtmlAttributes"]["max"] == 86400
    for name in ("engine", "include_shape", "motion_correction", "stage_timeout_seconds"):
        assert cells[name].node_id == "extract_motion"
        assert cells[name].required is False


def test_download_is_portable_and_shape_is_independent():
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(prompt, {"body": "neutral", "betas": "0,1", "width": "640"})
    assert prompt["extract_motion"]["class_type"] == "LF_VideoToMotion"
    assert prompt["extract_motion"]["inputs"] == {
        "video_path": "video.mp4", "engine": "ExMR", "static_camera": True,
        "smoothing": True, "gpu_index": 0, "include_shape": False,
        "stage_timeout_seconds": 0.0, "motion_correction": True,
        "ground_feet": True, "push_in": "auto", "planted_seconds": "",
    }
    assert prompt["render_motion"]["inputs"] == {
        "motion_file": ["extract_motion", 0], "body": "neutral", "betas": "0,1",
        "width": 640, "height": 560, "source_video": "video.mp4",
    }
    assert set(prompt) == {"extract_motion", "render_motion"}


def test_run_resolves_one_video_and_reuses_it_for_comparison(tmp_path, monkeypatch):
    video = tmp_path / "shot.mp4"
    video.write_bytes(b"offline fixture")
    monkeypatch.setattr(workflow_module, "resolve_upload_paths", lambda *_a, **_k: [str(video)])
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {"video_path": [video], "smoothing": False})
    assert prompt["extract_motion"]["inputs"]["video_path"] == str(video)
    assert prompt["render_motion"]["inputs"]["source_video"] == str(video)
    assert prompt["extract_motion"]["inputs"]["smoothing"] is False


@pytest.mark.parametrize("configure_name", ["configure_prompt", "configure_download"])
def test_all_capture_options_are_forwarded(configure_name, tmp_path, monkeypatch):
    video = tmp_path / "shot.mp4"
    video.write_bytes(b"offline fixture")
    monkeypatch.setattr(workflow_module, "resolve_upload_paths", lambda *_a, **_k: [str(video)])
    prompt = WORKFLOW.load_prompt()
    getattr(WORKFLOW, configure_name)(prompt, {
        "video_path": [video], "engine": "ExMR", "static_camera": False,
        "smoothing": False, "gpu_index": "2", "include_shape": True,
        "stage_timeout_seconds": "17.5", "motion_correction": True,
        "ground_feet": True, "push_in": "yes", "planted_seconds": "1-2",
    })
    assert prompt["extract_motion"]["inputs"] == {
        "video_path": str(video) if configure_name == "configure_prompt" else "video.mp4",
        "engine": "ExMR", "static_camera": False, "smoothing": False,
        "gpu_index": 2, "include_shape": True, "stage_timeout_seconds": 17.5,
        "motion_correction": True, "ground_feet": True, "push_in": "yes", "planted_seconds": "1-2",
    }
    assert prompt["render_motion"]["inputs"]["motion_file"] == ["extract_motion", 0]


@pytest.mark.parametrize("timeout,expected", [(None, 0.0), ("", 0.0), (0, 0.0), ("0", 0.0), (86400, 86400.0)])
def test_timeout_accepts_automatic_and_upper_bound(timeout, expected):
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(prompt, {"stage_timeout_seconds": timeout})
    assert prompt["extract_motion"]["inputs"]["stage_timeout_seconds"] == expected


def test_multiple_uploads_are_rejected(monkeypatch):
    monkeypatch.setattr(workflow_module, "resolve_upload_paths", lambda *_a, **_k: ["a.mp4", "b.mp4"])
    with pytest.raises(InputValidationError, match="video_path"):
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {"video_path": ["a.mp4", "b.mp4"]})


@pytest.mark.parametrize("inputs,field", [
    ({"body": "other"}, "body"), ({"betas": "nan"}, "betas"),
    ({"betas": ""}, "betas"), ({"betas": ",".join(["0"] * 11)}, "betas"),
    ({"static_camera": "true"}, "static_camera"), ({"smoothing": 1}, "smoothing"),
    ({"width": "0"}, "width"), ({"width": "321"}, "width"),
    ({"height": "561"}, "height"), ({"gpu_index": True}, "gpu_index"),
    ({"engine": "GVHMR"}, "engine"), ({"include_shape": "true"}, "include_shape"),
    ({"motion_correction": "true"}, "motion_correction"),
    ({"ground_feet": 1}, "ground_feet"), ({"push_in": "maybe"}, "push_in"),
    ({"planted_seconds": "soon"}, "planted_seconds"), ({"planted_seconds": 3}, "planted_seconds"),
    ({"planted_seconds": "1-2", "motion_correction": False}, "planted_seconds"),
    ({"stage_timeout_seconds": True}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": -1}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": "nan"}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": float("inf")}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": "invalid"}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": 86401}, "stage_timeout_seconds"),
])
def test_invalid_controls_fail_before_upload_resolution(inputs, field):
    with pytest.raises(ValueError, match=field):
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), inputs)


@pytest.mark.parametrize("name", ["glb_path", "bone_map_path"])
def test_optional_target_upload_controls(name):
    cell = next(cell for cell in WORKFLOW.inputs if cell.id == name)
    assert cell.shape == "upload" and cell.required is False
    assert cell.node_id == "retarget_motion"
    assert cell.props["lfHtmlAttributes"]["accept"] == (".glb" if name == "glb_path" else ".json")


@pytest.mark.parametrize("value", [None, "", []])
def test_empty_optional_target_leaves_default_graph_exact(value):
    from copy import deepcopy
    prompt = WORKFLOW.load_prompt()
    expected = deepcopy(prompt)
    WORKFLOW.configure_download(prompt, {"glb_path": value, "bone_map_path": value})
    assert prompt == expected


@pytest.mark.parametrize("provided,missing", [("glb_path", "bone_map_path"), ("bone_map_path", "glb_path")])
def test_partial_target_upload_pair_is_rejected(provided, missing):
    with pytest.raises(InputValidationError, match=missing):
        WORKFLOW.configure_download(WORKFLOW.load_prompt(), {provided: "target.glb"})


def test_target_download_is_portable_and_forwards_independent_body():
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(prompt, {"glb_path": ["any-rig.glb"], "bone_map_path": ["any-map.json"],
                                         "body": "male", "betas": "1,2"})
    assert prompt["retarget_motion"] == {
        "class_type": "LF_RetargetMotion",
        "inputs": {"motion_file": ["extract_motion", 0], "body": "male", "betas": "1,2",
                   "glb_path": "target.glb", "bone_map_path": "bone-map.json",
                   "keep_rest_facing": "[]", "flatten_slope": "[]"},
        "_meta": {"title": "Retarget motion onto the uploaded rig"},
    }
    assert prompt["render_motion"]["inputs"]["body_glb"] == ["retarget_motion", 0]
    assert prompt["render_motion"]["inputs"]["motion_file"] == ["extract_motion", 0]
    assert "any-rig" not in str(prompt) and "any-map" not in str(prompt)


def test_target_run_resolves_exactly_one_file_for_each_upload(tmp_path, monkeypatch):
    files = {name: tmp_path / filename for name, filename in
             (("video_path", "video.mp4"), ("glb_path", "rig.glb"), ("bone_map_path", "map.json"))}
    for path in files.values():
        path.write_bytes(b"synthetic upload")
    calls = []
    def resolve(_inputs, name, **kwargs):
        calls.append((name, kwargs))
        return [str(files[name])]
    monkeypatch.setattr(workflow_module, "resolve_upload_paths", resolve)
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {name: [path] for name, path in files.items()})
    assert prompt["retarget_motion"]["inputs"]["glb_path"] == str(files["glb_path"])
    assert prompt["retarget_motion"]["inputs"]["bone_map_path"] == str(files["bone_map_path"])
    assert [name for name, _ in calls] == ["video_path", "glb_path", "bone_map_path"]


@pytest.mark.parametrize("glb,bone_map,field", [
    (["a.glb", "b.glb"], ["map.json"], "glb_path"),
    (["a.glb"], ["a.json", "b.json"], "bone_map_path"),
    (["a.obj"], ["map.json"], "glb_path"),
    (["a.glb"], ["map.txt"], "bone_map_path"),
])
def test_target_upload_cardinality_and_extensions(glb, bone_map, field):
    with pytest.raises(InputValidationError, match=field):
        WORKFLOW.configure_download(WORKFLOW.load_prompt(), {"glb_path": glb, "bone_map_path": bone_map})
