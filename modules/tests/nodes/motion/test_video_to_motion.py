"""CPU synthetic contracts; application/GPU execution belongs to acceptance."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace
import types

import pytest

from modules.nodes.motion import video_to_motion as node_module
from modules.utils.helpers.motion import rgb_mocap as adapter
from modules.utils.helpers.motion import rgb_mocap_bridge as bridge_module
from modules.utils.helpers.motion.format import JOINT_NAMES, POSE_WIDTHS, read_motion, validate_motion


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
    assert schema["optional"]["stage_timeout_seconds"][0] == "FLOAT"
    assert schema["optional"]["stage_timeout_seconds"][1]["default"] == 0.0
    # Appended last: saved graphs keep their widget order.
    assert list(schema["optional"]) == ["include_shape", "ui_widget", "stage_timeout_seconds", "motion_correction",
                                        "ground_feet", "push_in", "planted_seconds"]
    assert schema["optional"]["motion_correction"][0] == "BOOLEAN"
    assert schema["optional"]["motion_correction"][1]["default"] is True
    assert schema["optional"]["ground_feet"][0] == "BOOLEAN"
    assert schema["optional"]["ground_feet"][1]["default"] is True
    assert schema["optional"]["push_in"][0] == ["auto", "yes", "no"]
    assert schema["optional"]["push_in"][1]["default"] == "auto"
    assert schema["optional"]["planted_seconds"][0] == "STRING"
    assert schema["optional"]["planted_seconds"][1]["default"] == ""
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
        assert options["stage_timeout_seconds"] == 0.0
        assert options["motion_correction"] is True
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
    ({"motion_correction": 1}, "motion_correction must be a boolean"),
    ({"ground_feet": "yes"}, "ground_feet must be a boolean"),
    ({"push_in": True}, "push_in must be auto, yes or no"),
    ({"planted_seconds": "1.5"}, "planted_seconds needs spans"),
    ({"planted_seconds": "2-1"}, "must run forward"),
    ({"planted_seconds": "1-2", "ground_feet": False}, "turn on motion_correction and ground_feet"),
    ({"planted_seconds": "1-2", "motion_correction": False}, "turn on motion_correction and ground_feet"),
    ({"stage_timeout_seconds": -1}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": True}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": float("inf")}, "stage_timeout_seconds"),
    ({"stage_timeout_seconds": float("nan")}, "stage_timeout_seconds"),
])
def test_invalid_controls_fail_before_installation(tmp_path, options, message):
    with pytest.raises(ValueError, match=message):
        adapter.run_video_to_motion("missing.mp4", tmp_path, **options)


@pytest.mark.parametrize("motion_correction", [True, False])
def test_capture_pipeline_preserves_motion_and_explicit_shape(tmp_path, monkeypatch, motion_correction):
    source = tmp_path / "source.mp4"
    source.touch()
    monkeypatch.setattr(adapter, "installation_path", lambda: tmp_path)
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    monkeypatch.setattr(adapter, "_cuda_preflight", lambda *args: None)
    monkeypatch.setattr(adapter, "_clip_duration", lambda *args: 2.0)
    calls = []
    motion = motion_fixture()
    corrected = motion_fixture()
    corrected["world"]["transl"] = [[0.0, -0.18, 0.0]] * 4
    correction = {"result": "corrected_initial", "floor": 0.003, "warning": "", "options": {"mode": "flat"}}
    def bridge(root, job, action, request, profile, progress):
        calls.append((action, profile, dict(request)))
        assert job.is_relative_to(tmp_path)
        if action == "prepare":
            return {"project_dir": str(job / "project" / "exmr")}
        if action == "capture":
            return {"motion": motion, "frame_count": 4}
        if action == "correct":
            return {"motion": corrected, "frame_count": 4, "correction": correction}
        if action == "export":
            return {"bvh_file": str(job / "motion.bvh"), "fbx_file": str(job / "motion.fbx")}
        return {}
    monkeypatch.setattr(adapter, "_run_bridge", bridge)
    output = adapter.run_video_to_motion(source, tmp_path, motion_correction=motion_correction)
    stages = [("prepare", "shared"), ("track", "shared"), ("capture", "exmr"), ("export", "shared")]
    if motion_correction:
        stages.insert(3, ("correct", "shared"))
    assert [(stage, profile) for stage, profile, _ in calls] == stages
    assert calls[0][2]["include_shape"] is False
    # Every stage, the export included, names the one result the motion file carries.
    assert {request["result"] for _, _, request in calls} == {"corrected_initial" if motion_correction else "initial"}
    saved = read_motion(output["motion_file"])
    assert saved == (corrected if motion_correction else motion)
    assert "betas" not in saved
    assert len(saved["world"]["left_hand_pose"][0]) == 45
    assert output["motion_correction"] is motion_correction
    assert output.get("correction") == (correction if motion_correction else None)
    # Grounding rides on the correction, read from the data by default.
    assert {request["ground_feet"] for _, _, request in calls} == {motion_correction}
    assert output["ground_feet"] is motion_correction
    assert {request["push_in"] for _, _, request in calls} == {None}
    assert {tuple(map(tuple, request["planted_seconds"])) for _, _, request in calls} == {()}


def test_grounding_options_reach_every_stage(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.touch()
    monkeypatch.setattr(adapter, "installation_path", lambda: tmp_path)
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    monkeypatch.setattr(adapter, "_cuda_preflight", lambda *args: None)
    monkeypatch.setattr(adapter, "_clip_duration", lambda *args: 6.0)
    requests = []
    def bridge(root, job, action, request, profile, progress):
        requests.append(dict(request))
        if action == "prepare":
            return {"project_dir": str(job / "project" / "exmr")}
        if action in ("capture", "correct"):
            return {"motion": motion_fixture(), "frame_count": 4, "correction": {}}
        if action == "export":
            return {"bvh_file": str(job / "motion.bvh"), "fbx_file": str(job / "motion.fbx")}
        return {}
    monkeypatch.setattr(adapter, "_run_bridge", bridge)
    adapter.run_video_to_motion(source, tmp_path, push_in="yes", planted_seconds="1.65-2.3; 4-5")
    assert {request["push_in"] for request in requests} == {True}
    assert requests[-1]["planted_seconds"] == [[1.65, 2.3], [4.0, 5.0]]
    adapter.run_video_to_motion(source, tmp_path, push_in="no", ground_feet=False)
    assert requests[-1]["push_in"] is False and requests[-1]["ground_feet"] is False


def test_planted_spans_parse_commas_and_semicolons():
    assert adapter.planted_spans("") == []
    assert adapter.planted_spans(" 0-0.5 , 1.25-2 ;3-4 ") == [[0.0, 0.5], [1.25, 2.0], [3.0, 4.0]]


def test_stage_failure_does_not_continue_to_export(tmp_path, monkeypatch):
    source = tmp_path / "source.mp4"
    source.touch()
    monkeypatch.setattr(adapter, "installation_path", lambda: tmp_path)
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    monkeypatch.setattr(adapter, "_cuda_preflight", lambda *args: None)
    monkeypatch.setattr(adapter, "_clip_duration", lambda *args: 2.0)
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


@pytest.fixture
def bridge_worker(tmp_path, monkeypatch):
    """Use real isolated processes; substitute only the application entry script."""
    worker = tmp_path / "synthetic_worker.py"
    launch = subprocess.Popen
    calls = []

    def popen(command, **kwargs):
        calls.append(list(command))
        command = list(command)
        command[5] = str(worker)
        return launch(command, **kwargs)

    monkeypatch.setattr(adapter, "runtime_python", lambda *args: Path(sys.executable))
    monkeypatch.setattr(adapter.subprocess, "Popen", popen)

    def write(source):
        worker.write_text(source, encoding="utf-8", newline="\n")
        return calls
    return write


def test_worker_error_names_stage_and_retains_log(tmp_path, bridge_worker):
    bridge_worker(
        "import sys\n"
        + "print(" + repr(adapter.PREFIX + json.dumps({"type": "failed", "message": "prepare required models first"})) + ", flush=True)\n"
        + "sys.exit(3)\n"
    )
    with pytest.raises(RuntimeError, match="RGB MoCap capture failed: prepare required models first"):
        adapter._run_bridge(tmp_path, tmp_path, "capture", {"gpu_index": 0, "stage_timeout_seconds": 10}, "exmr", None)
    assert "prepare required models first" in (tmp_path / "capture.log").read_text(encoding="utf-8")


def test_worker_timeout_stops_real_sleeping_worker_and_child(tmp_path, bridge_worker):
    child_code = "import pathlib,time; pathlib.Path('child_ready').touch(); time.sleep(120)"
    calls = bridge_worker(
        "import json, pathlib, subprocess, sys, time\n"
        f"child = subprocess.Popen([sys.executable, '-B', '-I', '-c', {child_code!r}])\n"
        "pathlib.Path('pids.json').write_text(json.dumps([__import__('os').getpid(), child.pid]), encoding='utf-8')\n"
        "print('sleeping worker with child', flush=True)\n"
        "time.sleep(120)\n"
    )
    started = time.monotonic()
    with pytest.raises(RuntimeError, match=r"capture timed out after .*limit 2 seconds.*no retry.*capture.log"):
        adapter._run_bridge(tmp_path, tmp_path, "capture", {"gpu_index": 0, "stage_timeout_seconds": 2}, "exmr", None)
    assert time.monotonic() - started < 8
    assert len(calls) == 1
    assert (tmp_path / "child_ready").exists()
    pids = json.loads((tmp_path / "pids.json").read_text(encoding="utf-8"))
    for pid in pids:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            kernel = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
            kernel.WaitForSingleObject.restype = wintypes.DWORD
            kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
            handle = kernel.OpenProcess(0x00100000, False, pid)
            if handle:
                try:
                    assert kernel.WaitForSingleObject(handle, 1000) == 0
                finally:
                    kernel.CloseHandle(handle)
        else:
            # waitpid can reap our worker; a killed grandchild may briefly be a zombie.
            status = Path(f"/proc/{pid}/stat")
            assert not status.exists() or status.read_text(encoding="utf-8").split()[2] == "Z"
    log = (tmp_path / "capture.log").read_text(encoding="utf-8")
    assert "sleeping worker with child" in log
    assert "worker process tree stopped; no retry" in log


def test_timeout_diagnostic_survives_native_stop_error(tmp_path, bridge_worker, monkeypatch):
    from contextlib import contextmanager

    bridge_worker("import time; time.sleep(120)\n")
    contain = adapter._worker_tree

    @contextmanager
    def reported_failure(process):
        with contain(process) as stop:
            def fail_after_stopping():
                stop()
                raise OSError("synthetic native tree stop failure")
            yield fail_after_stopping

    monkeypatch.setattr(adapter, "_worker_tree", reported_failure)
    with pytest.raises(RuntimeError, match=r"capture timed out after .*limit 0.2 seconds.*tree stop failed.*no retry.*capture.log"):
        adapter._run_bridge(tmp_path, tmp_path, "capture",
                            {"gpu_index": 0, "stage_timeout_seconds": 0.2}, "exmr", None)


def test_worker_streams_progress_and_result_while_retaining_log(tmp_path, bridge_worker):
    calls = bridge_worker(
        "import json, os, time\n"
        + "print('plain diagnostic', flush=True)\n"
        + "print(" + repr(adapter.PREFIX + json.dumps({"type": "progress", "message": "Capturing"})) + ", flush=True)\n"
        + "time.sleep(0.15)\n"
        + "print(" + repr(adapter.PREFIX + json.dumps({"type": "result", "result": {"done": True}})) + ", flush=True)\n"
    )
    events = []
    output = adapter._run_bridge(tmp_path, tmp_path, "capture",
                                {"gpu_index": 0, "stage_timeout_seconds": 10}, "exmr", events.append)
    assert output == {"done": True}
    assert [event["type"] for event in events] == ["progress", "result"]
    assert len(calls) == 1
    assert "plain diagnostic" in (tmp_path / "capture.log").read_text(encoding="utf-8")


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


def test_neutral_export_representation_is_not_rewritten(tmp_path, monkeypatch):
    """Motion Correction stamps hmr4d_results.pt, so the export's own pass must not rewrite it again."""
    import torch
    mocap = types.ModuleType("mocap")
    engines = types.ModuleType("mocap.engines")
    saves = []
    engines.save_tensor = lambda parameters, path: saves.append(path) or torch.save(parameters, path)
    mocap.engines = engines
    monkeypatch.setitem(sys.modules, "mocap", mocap)
    monkeypatch.setitem(sys.modules, "mocap.engines", engines)
    source = tmp_path / "hmr4d_results.pt"
    torch.save({space: {"betas": torch.ones(4, 10)} for space in ("smpl_params_global", "smpl_params_incam")}, source)
    bridge_module.prepare_export_parameters(tmp_path, False)
    neutral = source.read_bytes()
    bridge_module.prepare_export_parameters(tmp_path, False)
    assert source.read_bytes() == neutral
    assert saves == [source]


def test_corrected_result_carries_the_app_default_correction(monkeypatch):
    settings = types.ModuleType("mocap.correction_settings")
    settings.correction_options = lambda options=None: {"auto_floor": True, "preset": "normal", "mode": "flat",
                                                        "foot_lock": True, "hand_lock": False}
    monkeypatch.setitem(sys.modules, "mocap", types.ModuleType("mocap"))
    monkeypatch.setitem(sys.modules, "mocap.correction_settings", settings)
    state = bridge_module.select_result({"frames": 4}, "corrected_initial")
    assert state == {"frames": 4, "pipeline": {"model": "exmr", "result": "corrected_initial"},
                     "correction": settings.correction_options()}
    assert bridge_module.select_result({"frames": 4}, "initial") == {
        "frames": 4, "pipeline": {"model": "exmr", "result": "initial"}}


def synthetic_capture(yaw, frames=3):
    """ExMR's world and camera results and a corrected record, the camera turned by a known yaw."""
    import numpy as np
    import torch
    from scipy.spatial.transform import Rotation
    rng = np.random.default_rng(7)
    tensor = lambda value: torch.tensor(np.asarray(value), dtype=torch.float32)
    random = lambda width: tensor(rng.normal(scale=0.3, size=(frames, width)))
    orient = rng.normal(scale=0.3, size=(frames, 3))
    turn = Rotation.from_euler("y", yaw, degrees=True)
    world = dict(global_orient=tensor(orient), transl=random(3), body_pose=random(63), betas=random(10),
                 left_hand_pose=random(45), right_hand_pose=random(45))
    camera = dict(global_orient=tensor((turn * Rotation.from_rotvec(orient)).as_rotvec()), transl=random(3),
                  body_pose=random(63), betas=world["betas"], left_hand_pose=random(45), right_hand_pose=random(45))
    shift = torch.tensor([[0.01, -0.18, 0.02]] * frames)
    corrected = dict(global_orient=world["global_orient"].clone(), transl=world["transl"] + shift,
                     body_pose=random(63), betas=world["betas"], left_hand_pose=random(45), right_hand_pose=random(45))
    return {"fps": 30.0, "smplx_global": world, "smplx_incam": camera}, corrected


@pytest.mark.parametrize("yaw,seen", [(0.0, [0.01, -0.18, 0.02]), (90.0, [0.02, -0.18, -0.01])])
def test_corrected_motion_moves_the_camera_root_by_the_rotated_shift(yaw, seen):
    import numpy as np
    native, corrected = synthetic_capture(yaw)
    motion = validate_motion(bridge_module.corrected_motion(native, corrected, JOINT_NAMES, False))
    world, camera = native["smplx_global"], native["smplx_incam"]
    def close(value, expected):
        np.testing.assert_allclose(np.asarray(value), np.asarray(expected, dtype=np.float64), atol=1e-5)
    close(motion["world"]["global_orient"], world["global_orient"])
    close(motion["world"]["transl"], corrected["transl"])
    close(motion["camera"]["global_orient"], camera["global_orient"])
    # The correction's root shift, turned into the camera: a quarter yaw carries its x into -z.
    close(np.asarray(motion["camera"]["transl"]) - camera["transl"].numpy(), [seen] * 3)
    for space in ("world", "camera"):
        close(motion[space]["body_pose"], corrected["body_pose"])
        for hand in ("left_hand_pose", "right_hand_pose"):
            close(motion[space][hand], world[hand])  # ExMR's flat hands, never the corrected record's
    assert "betas" not in motion
    shaped = bridge_module.corrected_motion(native, corrected, JOINT_NAMES, True)
    close(shaped["betas"], world["betas"][:1])


def test_corrected_motion_refuses_another_capture():
    native, corrected = synthetic_capture(0.0)
    corrected["global_orient"] = corrected["global_orient"] + 0.1
    with pytest.raises(RuntimeError, match="does not match this ExMR capture"):
        bridge_module.corrected_motion(native, corrected, JOINT_NAMES, False)


def test_git_missing_from_path_is_actionable(tmp_path, monkeypatch):
    (tmp_path / "worker_boot.py").touch()
    monkeypatch.setenv("RGB_MOCAP_PATH", str(tmp_path))
    monkeypatch.setenv("PATH", str(tmp_path / "no_git_here"))
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match="requires git on ComfyUI's PATH.*Install Git"):
        adapter.installation_path()


def test_capture_setting_has_one_owner_and_is_read_at_execution(tmp_path, monkeypatch):
    from modules.workflow_runner.config import Settings

    assert "RGB_MOCAP_PATH" not in Settings.__dataclass_fields__
    roots = [tmp_path / "first", tmp_path / "second"]
    for root in roots:
        root.mkdir()
        (root / "worker_boot.py").touch()
    calls = []
    monkeypatch.setattr(adapter.subprocess, "run", lambda command, **kwargs:
                        calls.append(command) or SimpleNamespace(returncode=0, stdout=adapter.SUPPORTED_COMMIT))
    for root in roots:
        monkeypatch.setenv("RGB_MOCAP_PATH", str(root))
        assert adapter.installation_path() == root.resolve()
    assert [call[2] for call in calls] == [str(root.resolve()) for root in roots]


@pytest.mark.parametrize("devices,index", [([], 0), (["Synthetic GPU"], 1)])
def test_cuda_unavailable_or_index_fails_before_job_creation(tmp_path, monkeypatch, devices, index):
    source = tmp_path / "source.mp4"
    source.touch()
    monkeypatch.setattr(adapter, "installation_path", lambda: tmp_path)
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    monkeypatch.setattr(adapter.subprocess, "run", lambda *args, **kwargs:
                        SimpleNamespace(returncode=0, stdout=adapter.PREFIX + json.dumps(devices), stderr=""))
    with pytest.raises(RuntimeError, match=f"gpu_index={index}.*available CUDA devices") as failure:
        adapter.run_video_to_motion(source, tmp_path / "output", gpu_index=index)
    assert ("none" if not devices else "0: Synthetic GPU") in str(failure.value)
    assert not (tmp_path / "output").exists()


def test_cuda_probe_uses_app_runtime_and_physical_order(tmp_path, monkeypatch):
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "7")
    monkeypatch.setenv("CUDA_DEVICE_ORDER", "FASTEST_FIRST")
    monkeypatch.setattr(adapter, "runtime_python", lambda root, profile: tmp_path / profile / "python.exe")
    calls = []
    def run(command, **options):
        calls.append((command, options))
        return SimpleNamespace(returncode=0, stdout=adapter.PREFIX + '["GPU A", "GPU B"]', stderr="")
    monkeypatch.setattr(adapter.subprocess, "run", run)
    adapter._cuda_preflight(tmp_path, 1)
    command, options = calls[0]
    assert command[0] == str(tmp_path / "exmr" / "python.exe")
    assert command[1:6] == ["-B", "-I", "-X", "utf8", "-c"]
    assert "import json, torch" in command[-1]
    assert options["env"]["CUDA_DEVICE_ORDER"] == "PCI_BUS_ID"
    assert "CUDA_VISIBLE_DEVICES" not in options["env"]
    assert options["timeout"] == 30
    assert os.environ["CUDA_VISIBLE_DEVICES"] == "7"


def test_cuda_probe_timeout_names_index_and_recovery(tmp_path, monkeypatch):
    monkeypatch.setattr(adapter, "runtime_python", lambda *args: tmp_path / "python.exe")
    def run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 30)
    monkeypatch.setattr(adapter.subprocess, "run", run)
    with pytest.raises(RuntimeError, match="gpu_index=2.*timed out after 30 seconds.*available devices"):
        adapter._cuda_preflight(tmp_path, 2)


@pytest.mark.parametrize("action,short,long", [
    ("prepare", 120, 400), ("track", 300, 3000),
    ("capture", 600, 12000), ("correct", 300, 2000), ("export", 300, 2000),
])
def test_stage_bounds_scale_with_duration_and_honor_override(action, short, long):
    assert adapter._stage_timeout(action, {"duration_seconds": 1}) == short
    assert adapter._stage_timeout(action, {"duration_seconds": 100}) == long
    assert adapter._stage_timeout(action, {"duration_seconds": 100, "stage_timeout_seconds": 17.5}) == 17.5


def test_clip_duration_reads_real_video_metadata(tmp_path):
    import av
    import numpy as np
    source = tmp_path / "source.mp4"
    with av.open(str(source), mode="w") as video:
        stream = video.add_stream("libx264", rate=30)
        stream.width, stream.height, stream.pix_fmt = 64, 64, "yuv420p"
        for _ in range(6):
            frame = av.VideoFrame.from_ndarray(np.zeros((64, 64, 3), dtype=np.uint8), format="rgb24")
            for packet in stream.encode(frame):
                video.mux(packet)
        for packet in stream.encode():
            video.mux(packet)
    assert adapter._clip_duration(source) == pytest.approx(0.2)
