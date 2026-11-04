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


def test_download_is_portable_and_shape_is_independent():
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_download(prompt, {"body": "neutral", "betas": "0,1", "width": "640"})
    assert prompt["extract_motion"]["class_type"] == "LF_VideoToMotion"
    assert prompt["extract_motion"]["inputs"] == {
        "video_path": "video.mp4", "engine": "ExMR", "static_camera": True,
        "smoothing": True, "gpu_index": 0, "include_shape": False,
    }
    assert prompt["render_motion"]["inputs"] == {
        "motion_file": ["extract_motion", 0], "body": "neutral", "betas": "0,1",
        "width": 640, "height": 560, "source_video": "video.mp4",
    }


def test_run_resolves_one_video_and_reuses_it_for_comparison(tmp_path, monkeypatch):
    video = tmp_path / "shot.mp4"
    video.write_bytes(b"offline fixture")
    monkeypatch.setattr(workflow_module, "resolve_upload_paths", lambda *_a, **_k: [str(video)])
    prompt = WORKFLOW.load_prompt()
    WORKFLOW.configure_prompt(prompt, {"video_path": [video], "smoothing": False})
    assert prompt["extract_motion"]["inputs"]["video_path"] == str(video)
    assert prompt["render_motion"]["inputs"]["source_video"] == str(video)
    assert prompt["extract_motion"]["inputs"]["smoothing"] is False


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
])
def test_invalid_controls_fail_before_upload_resolution(inputs, field):
    with pytest.raises(ValueError, match=field):
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), inputs)
