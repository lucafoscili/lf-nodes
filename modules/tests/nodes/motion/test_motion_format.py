from __future__ import annotations

from copy import deepcopy
import json

import numpy as np
import pytest

from modules.utils.helpers.motion.format import (
    JOINT_NAMES,
    read_motion,
    validate_motion,
    write_motion,
)


def synthetic_motion(count: int = 3) -> dict:
    """A portable clip with visibly distinct frame values and no model data."""
    pose = {
        name: (np.arange(count * width).reshape(count, width) / 100).tolist()
        for name, width in {
            "global_orient": 3,
            "transl": 3,
            "body_pose": 63,
            "left_hand_pose": 45,
            "right_hand_pose": 45,
        }.items()
    }
    return {
        "schema": "lf.motion.v1",
        "fps": 29.97,
        "joint_names": deepcopy(JOINT_NAMES),
        "world": deepcopy(pose),
        "camera": deepcopy(pose),
        "betas": [[0.25] * 10],
    }


def test_motion_json_round_trip_preserves_both_spaces_and_frame_order(tmp_path) -> None:
    motion = synthetic_motion()
    motion["camera"]["transl"][1][0] = -0.125
    motion["label"] = "Synthetic café"
    path = tmp_path / "motion.json"

    write_motion(path, motion)

    assert read_motion(path) == motion
    assert json.loads(path.read_text(encoding="utf-8")) == motion
    assert path.read_bytes().endswith(b"\n")
    assert b"\r" not in path.read_bytes()


@pytest.mark.parametrize("schema", [None, "lf.motion.v2", "smplx"])
def test_motion_rejects_unknown_schema(schema) -> None:
    motion = synthetic_motion()
    motion["schema"] = schema
    with pytest.raises(ValueError, match="schema"):
        validate_motion(motion)


def test_motion_rejects_reordered_joint_names() -> None:
    motion = synthetic_motion()
    motion["joint_names"]["body"].reverse()
    with pytest.raises(ValueError, match="joint_names"):
        validate_motion(motion)


@pytest.mark.parametrize("fps", [None, "bad", 0, -1, float("nan"), float("inf")])
def test_motion_rejects_invalid_fps(fps) -> None:
    motion = synthetic_motion()
    motion["fps"] = fps
    with pytest.raises(ValueError, match="fps"):
        validate_motion(motion)


@pytest.mark.parametrize("space", ["camera", "world"])
@pytest.mark.parametrize(
    ("values", "message"),
    [
        ([0, 0, 0], "shape"),
        ([[0, 0]], "shape"),
        ([], "shape"),
        ([[0, 0, 0]], "frame count"),
        ([[float("nan"), 0, 0]] * 3, "non-finite"),
        ([[float("inf"), 0, 0]] * 3, "non-finite"),
        ([["bad", 0, 0]] * 3, "numeric frame array"),
    ],
)
def test_motion_rejects_unusable_pose_arrays(space, values, message) -> None:
    motion = synthetic_motion()
    motion[space]["transl"] = values
    with pytest.raises(ValueError, match=message):
        validate_motion(motion)


@pytest.mark.parametrize("space,field", [("world", "body_pose"), ("camera", "right_hand_pose")])
def test_motion_rejects_missing_required_parameters(space, field) -> None:
    motion = synthetic_motion()
    del motion[space][field]
    with pytest.raises(ValueError, match=f"{space}.{field}"):
        validate_motion(motion)


@pytest.mark.parametrize("betas", [[0] * 10, [[0] * 9], [[0] * 10] * 2, [[float("inf")] * 10], {"bad": 1}, [[0], [0, 1]]])
def test_motion_rejects_invalid_shape_coefficients(betas) -> None:
    motion = synthetic_motion()
    motion["betas"] = betas
    with pytest.raises(ValueError, match="betas"):
        validate_motion(motion)


def test_motion_accepts_per_frame_or_absent_shape_coefficients() -> None:
    motion = synthetic_motion()
    motion["betas"] = [[index] * 10 for index in range(3)]
    assert validate_motion(motion) is motion
    del motion["betas"]
    assert validate_motion(motion) is motion


def test_motion_read_reports_missing_and_invalid_json(tmp_path) -> None:
    path = tmp_path / "motion.json"
    with pytest.raises(FileNotFoundError, match="Motion file is missing"):
        read_motion(path)
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid motion JSON"):
        read_motion(path)


def test_motion_invalid_write_does_not_replace_existing_file(tmp_path) -> None:
    path = tmp_path / "motion.json"
    path.write_text("previous", encoding="utf-8")
    motion = synthetic_motion()
    motion["camera"]["body_pose"] = []
    with pytest.raises(ValueError, match="body_pose"):
        write_motion(path, motion)
    assert path.read_text(encoding="utf-8") == "previous"


@pytest.mark.parametrize("source_fps", [24, 60])
def test_capture_writer_keeps_working_frame_rate_and_source_time(tmp_path, monkeypatch, source_fps) -> None:
    """Exercise the bridge and JSON writer with synthetic native worker output."""
    import sys
    from types import ModuleType

    import torch

    from modules.utils.helpers.motion import rgb_mocap_bridge
    from modules.utils.helpers.motion.format import POSE_WIDTHS

    project = tmp_path / "project"
    project.mkdir()
    # The app prepares 60 working frames from a two-second source at either rate.
    (project / "project.json").write_text(json.dumps({
        "fps": 30, "frames": 60, "source": {"fps": source_fps, "frames": 2 * source_fps},
    }), encoding="utf-8")
    request_path = tmp_path / "capture_request.json"
    request_path.write_text(json.dumps({
        "project_dir": str(project), "joint_names": JOINT_NAMES, "include_shape": False,
    }), encoding="utf-8")

    mocap = ModuleType("mocap")
    for name in ("runtime_registry", "models", "paths", "exmr_backend", "batch_worker"):
        module = ModuleType("mocap." + name)
        setattr(mocap, name, module)
        monkeypatch.setitem(sys.modules, "mocap." + name, module)
    monkeypatch.setitem(sys.modules, "mocap", mocap)
    mocap.runtime_registry.activate = lambda *_: None
    mocap.exmr_backend.LINKS = {}
    mocap.models.BY_KEY = {}
    mocap.models.ready = lambda _: True

    def capture(arguments, observe):
        state = json.loads((project / "project.json").read_text(encoding="utf-8"))
        parameters = {key: torch.zeros(state["frames"], width) for key, width in POSE_WIDTHS.items()}
        parameters["transl"][:, 0] = torch.arange(state["frames"]) / state["fps"]
        # This is the pinned backend's output seam: native fps is project fps.
        torch.save({"fps": state["fps"], "smplx_global": parameters, "smplx_incam": parameters},
                   project / "exmr_results.pt")
        return 0

    mocap.batch_worker.main = capture
    monkeypatch.setattr(sys, "argv", ["bridge", str(tmp_path / "app"), str(tmp_path), "capture", str(request_path)])
    # Restore process environment after main sets its isolated-worker paths.
    monkeypatch.setenv("RGB_MOCAP_DATA", "")
    monkeypatch.setenv("RGB_MOCAP_MANAGED", "")
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    result = rgb_mocap_bridge.main()
    output = tmp_path / "motion.lf.json"
    write_motion(output, result["motion"])
    motion = read_motion(output)

    assert motion["fps"] == 30
    assert result["frame_count"] == len(motion["world"]["transl"]) == 60
    assert result["frame_count"] / motion["fps"] == 2
    np.testing.assert_allclose(
        np.asarray(motion["world"]["transl"])[:, 0], np.arange(60) / motion["fps"],
    )
    assert motion["world"]["transl"][30][0] == 30 / motion["fps"] == 1
    assert 30 / motion["fps"] * source_fps == source_fps
