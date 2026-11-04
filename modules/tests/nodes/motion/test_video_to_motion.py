"""CPU synthetic contracts; application/GPU execution belongs to acceptance."""

import json
from pathlib import Path
from types import SimpleNamespace
import types

import pytest

from modules.nodes.motion import video_to_motion as node_module
from modules.utils.helpers.motion import rgb_mocap as adapter
from modules.utils.helpers.motion import rgb_mocap_bridge as bridge_module
from modules.utils.helpers.motion.format import JOINT_NAMES, POSE_WIDTHS, read_motion


def motion_fixture():
    return dict(schema="lf.motion.v1", fps=30.0, joint_names=JOINT_NAMES,
                **{space: {key: [[0.0] * width for _ in range(4)]
                           for key, width in POSE_WIDTHS.items()}
                   for space in ("world", "camera")})


def test_schema_and_output_contract():
    node = node_module.LF_VideoToMotion
    schema = node.INPUT_TYPES()
    assert tuple(schema["required"]) == ("video_path", "engine", "static_camera", "smoothing", "gpu_index")
    assert schema["required"]["engine"] == (["ExMR"], {"default": "ExMR", "tooltip": "Uses the installed RGB MoCap ExMR runtime and registered models."})
    assert schema["required"]["static_camera"][1]["default"] is True
    assert schema["required"]["smoothing"][1]["default"] is True
    assert schema["required"]["gpu_index"][1]["default"] == 0
    assert schema["optional"]["include_shape"][1]["default"] is False
    assert schema["optional"]["ui_widget"][0] == "LF_CODE"
    assert node.INPUT_IS_LIST is False
    assert node.RETURN_TYPES == ("STRING",) * 4
    assert node.RETURN_NAMES == ("motion_file", "bvh_file", "fbx_file", "project_dir")
    assert node.OUTPUT_IS_LIST == (False,) * 4
    assert len(node.OUTPUT_TOOLTIPS) == 4


def test_headless_node_returns_live_and_durable_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(node_module.folder_paths, "get_output_directory", lambda: str(tmp_path))
    output = {key: str(tmp_path / value) for key, value in (
        ("motion_file", "motion.json"), ("bvh_file", "motion.bvh"),
        ("fbx_file", "motion.fbx"), ("project_dir", "project"))}
    output.update(engine="ExMR", frame_count=4, fps=30)
    calls = []
    def run(path, output_root, **options):
        assert path == "source.mp4"
        assert options["include_shape"] is False
        options["progress"]({"type": "progress", "message": "Capturing"})
        return output
    monkeypatch.setattr(node_module, "run_video_to_motion", run)
    monkeypatch.setattr(node_module, "safe_send_sync", lambda *args: calls.append(args))
    result = node_module.LF_VideoToMotion().on_exec("source.mp4", node_id=["17"])
    assert result["result"] == tuple(output[key] for key in node_module.LF_VideoToMotion.RETURN_NAMES)
    payload = result["ui"]["lf_output"][0]
    assert calls[-1] == ("videotomotion", payload, ["17"])
    assert json.loads(payload["value"]) == output
    assert payload["file_names"] == ["motion.json", "motion.bvh", "motion.fbx"]


def test_missing_installation_is_actionable(monkeypatch):
    monkeypatch.delenv("RGB_MOCAP_PATH", raising=False)
    with pytest.raises(RuntimeError, match="Set RGB_MOCAP_PATH"):
        adapter.installation_path()


def test_unsupported_revision_fails_before_runtime(tmp_path, monkeypatch):
    (tmp_path / "worker_boot.py").touch()
    monkeypatch.setenv("RGB_MOCAP_PATH", str(tmp_path))
    monkeypatch.setattr(adapter.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout="different\n"))
    with pytest.raises(RuntimeError, match="revision is unsupported"):
        adapter.installation_path()


def test_missing_runtime_is_actionable(tmp_path):
    with pytest.raises(RuntimeError, match="exmr runtime is missing"):
        adapter.runtime_python(tmp_path, "exmr")


@pytest.mark.parametrize("options,message", [
    ({"engine": "GVHMR"}, "engine must be ExMR"),
    ({"gpu_index": -1}, "gpu_index"),
    ({"gpu_index": True}, "gpu_index"),
    ({"smoothing": "global"}, "smoothing must be a boolean"),
])
def test_invalid_controls_fail_before_installation(tmp_path, options, message):
    with pytest.raises(ValueError, match=message):
        adapter.run_video_to_motion("missing.mp4", tmp_path, **options)


def test_capture_pipeline_preserves_motion_and_explicit_shape(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.touch()
    monkeypatch.setattr(adapter, "installation_path", lambda: tmp_path)
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    calls = []
    motion = motion_fixture()
    def bridge(root, job, action, request, profile, progress):
        calls.append((action, profile, dict(request)))
        assert job.is_relative_to(tmp_path)
        if action == "prepare":
            return {"project_dir": str(job / "project" / "exmr")}
        if action == "capture":
            return {"motion": motion, "frame_count": 4}
        if action == "export":
            return {"bvh_file": str(job / "motion.bvh"), "fbx_file": str(job / "motion.fbx")}
        return {}
    monkeypatch.setattr(adapter, "_run_bridge", bridge)
    output = adapter.run_video_to_motion(source, tmp_path)
    assert [(stage, profile) for stage, profile, _ in calls] == [
        ("prepare", "shared"), ("track", "shared"), ("capture", "exmr"), ("export", "shared")]
    assert calls[0][2]["include_shape"] is False
    saved = read_motion(output["motion_file"])
    assert saved == motion
    assert "betas" not in saved
    assert len(saved["world"]["left_hand_pose"][0]) == 45


def test_stage_failure_does_not_continue_to_export(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.touch()
    monkeypatch.setattr(adapter, "installation_path", lambda: tmp_path)
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    stages = []
    def bridge(root, job, action, request, profile, progress):
        stages.append(action)
        if action == "prepare":
            return {"project_dir": str(job / "project")}
        raise RuntimeError("Missing registered detector model; prepare models in RGB MoCap.")
    monkeypatch.setattr(adapter, "_run_bridge", bridge)
    with pytest.raises(RuntimeError, match="Missing registered detector"):
        adapter.run_video_to_motion(source, tmp_path)
    assert stages == ["prepare", "track"]


def test_worker_error_names_stage_and_retains_log(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: Path("python.exe"))
    class FailedProcess:
        stdout = iter([adapter.PREFIX + json.dumps({"type": "failed", "message": "prepare required models first"}) + "\n"])
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def wait(self):
            return 3
    monkeypatch.setattr(adapter.subprocess, "Popen", lambda *a, **k: FailedProcess())
    with pytest.raises(RuntimeError, match="RGB MoCap capture failed: prepare required models first"):
        adapter._run_bridge(tmp_path, tmp_path, "capture", {"gpu_index": 0}, "exmr", None)
    assert "prepare required models first" in (tmp_path / "capture.log").read_text(encoding="utf-8")


@pytest.mark.parametrize("model_ready", [True, False])
def test_cross_drive_model_aliases_copy_only_into_job(tmp_path, monkeypatch, model_ready):
    import sys
    source = tmp_path / "registered-weight.bin"
    source.write_bytes(b"synthetic weight")
    backend = types.ModuleType("mocap.exmr_backend")
    backend.LINKS = {"model": "body/model.bin"}
    models = types.ModuleType("mocap.models")
    models.BY_KEY = {"model": SimpleNamespace(path=source, name="Synthetic model")}
    models.ready = lambda _model: model_ready
    mocap = types.ModuleType("mocap")
    mocap.exmr_backend = backend
    monkeypatch.setitem(sys.modules, "mocap", mocap)
    monkeypatch.setitem(sys.modules, "mocap.exmr_backend", backend)
    monkeypatch.setitem(sys.modules, "mocap.models", models)
    def cross_drive(*args):
        raise OSError("cross-drive hardlink")
    monkeypatch.setattr(bridge_module.os, "link", cross_drive)
    job = tmp_path / "job"
    target = job / "runtime_data/cache/exmr/assets/body/model.bin"
    if not model_ready:
        with pytest.raises(RuntimeError, match="Prepare required RGB MoCap model Synthetic model:") as failure:
            bridge_module.prepare_exmr_assets(job)
        assert str(source) in str(failure.value)
        assert not target.exists()
        return
    bridge_module.prepare_exmr_assets(job)
    assert target.read_bytes() == source.read_bytes() == b"synthetic weight"
    assert backend.LINKS == {}


@pytest.mark.parametrize("include_shape", [False, True])
def test_export_shape_option_preserves_native_and_pose(tmp_path, monkeypatch, include_shape):
    import sys
    import torch
    mocap = types.ModuleType("mocap")
    engines = types.ModuleType("mocap.engines")
    engines.save_tensor = lambda parameters, path: torch.save(parameters, path)
    mocap.engines = engines
    monkeypatch.setitem(sys.modules, "mocap", mocap)
    monkeypatch.setitem(sys.modules, "mocap.engines", engines)
    source = tmp_path / "hmr4d_results.pt"
    native = tmp_path / "exmr_results.pt"
    native.write_bytes(b"native inference remains unchanged")
    record = {space: {"betas": torch.ones(4, 10), "body_pose": torch.ones(4, 63)}
              for space in ("smpl_params_global", "smpl_params_incam")}
    torch.save(record, source)
    original_bytes = source.read_bytes()
    bridge_module.prepare_export_parameters(tmp_path, include_shape)
    output = torch.load(source, map_location="cpu", weights_only=False)
    for space in record:
        assert torch.equal(output[space]["body_pose"], record[space]["body_pose"])
        expected = record[space]["betas"] if include_shape else torch.zeros(4, 10)
        assert torch.equal(output[space]["betas"], expected)
    assert native.read_bytes() == b"native inference remains unchanged"
    if include_shape:
        assert source.read_bytes() == original_bytes
