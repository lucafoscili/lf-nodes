"""Subprocess boundary for the separately installed RGB MoCap application."""

import json
import os
from pathlib import Path
import subprocess
import uuid

from ...env import str_env
from .format import JOINT_NAMES, write_motion


SUPPORTED_COMMIT = "ef05127a0dbddb3f3ac672a0722dddeae42ea651"
PREFIX = "@@LF_MOTION@@"


def installation_path():
    value = str_env("RGB_MOCAP_PATH").strip()
    if not value:
        raise RuntimeError("Set RGB_MOCAP_PATH to an installed RGB MoCap checkout.")
    root = Path(value).expanduser().resolve()
    if not (root / "worker_boot.py").is_file():
        raise RuntimeError(f"RGB_MOCAP_PATH is not an installed RGB MoCap checkout: {root}")
    revision = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if revision.returncode or revision.stdout.strip() != SUPPORTED_COMMIT:
        found = revision.stdout.strip() or "unavailable"
        raise RuntimeError(f"RGB MoCap revision is unsupported at {root}; found {found}; expected {SUPPORTED_COMMIT}.")
    return root


def runtime_python(root, profile):
    path = Path(root) / ("runtime_exmr" if profile == "exmr" else "runtime") / "python.exe"
    if not path.is_file():
        raise RuntimeError(f"RGB MoCap {profile} runtime is missing at {path}. Repair the app installation.")
    return path


def _run_bridge(root, job, action, request, profile, progress):
    request_path = job / (action + "_request.json")
    request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8", newline="\n")
    command = [str(runtime_python(root, profile)), "-B", "-I", "-X", "utf8",
               str(Path(__file__).with_name("rgb_mocap_bridge.py")),
               str(root), str(job), action, str(request_path)]
    environment = os.environ.copy()
    environment.update(CUDA_VISIBLE_DEVICES=str(request["gpu_index"]), CUDA_DEVICE_ORDER="PCI_BUS_ID",
                       PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1",
                       TRANSFORMERS_OFFLINE="1", WANDB_MODE="disabled")
    for key in ("TEMP", "TMP", "TMPDIR", "TORCH_HOME", "HF_HOME", "XDG_CACHE_HOME",
                "YOLO_CONFIG_DIR", "MPLCONFIGDIR", "CUDA_CACHE_PATH",
                "TORCHINDUCTOR_CACHE_DIR", "TRITON_CACHE_DIR"):
        directory = job / "runtime_data" / key.lower()
        directory.mkdir(parents=True, exist_ok=True)
        environment[key] = str(directory)
    log_path = job / (action + ".log")
    result = None
    failure = ""
    with log_path.open("w", encoding="utf-8", newline="\n") as log:
        with subprocess.Popen(command, cwd=str(job), env=environment,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              encoding="utf-8", errors="replace",
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)) as process:
            for line in process.stdout:
                log.write(line)
                log.flush()
                if not line.startswith(PREFIX):
                    continue
                event = json.loads(line[len(PREFIX):])
                if event.get("type") == "result":
                    result = event["result"]
                elif event.get("type") == "failed":
                    failure = event.get("message", "Worker failed")
                if progress:
                    progress(event)
            code = process.wait()
    if code or result is None:
        raise RuntimeError(f"RGB MoCap {action} failed: {failure or 'see worker log'}. Log: {log_path}")
    return result


def run_video_to_motion(video_path, output_root, *, engine="ExMR", static_camera=True,
                        smoothing=True, gpu_index=0, include_shape=False, progress=None):
    if engine != "ExMR":
        raise ValueError("engine must be ExMR.")
    if type(gpu_index) is not int or not 0 <= gpu_index <= 31:
        raise ValueError("gpu_index must be an integer from 0 to 31.")
    for name, value in (("static_camera", static_camera), ("smoothing", smoothing),
                        ("include_shape", include_shape)):
        if type(value) is not bool:
            raise ValueError(name + " must be a boolean.")
    source = Path(video_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError("video_path must name an existing local video file.")
    root = installation_path()
    runtime_python(root, "exmr")
    runtime_python(root, "shared")
    output_root = Path(output_root).resolve()
    job = output_root / "LF_Nodes" / "Motion" / ("capture_" + uuid.uuid4().hex[:12])
    if not job.resolve().is_relative_to(output_root):
        raise ValueError("Motion output directory escapes ComfyUI output.")
    job.mkdir(parents=True)
    request = dict(video_path=str(source), static_camera=static_camera,
                   smoothing=smoothing, gpu_index=gpu_index, include_shape=include_shape,
                   joint_names=JOINT_NAMES)
    prepared = _run_bridge(root, job, "prepare", request, "shared", progress)
    request["project_dir"] = prepared["project_dir"]
    _run_bridge(root, job, "track", request, "shared", progress)
    captured = _run_bridge(root, job, "capture", request, "exmr", progress)
    motion_file = job / "motion.lf.json"
    write_motion(motion_file, captured["motion"])
    exported = _run_bridge(root, job, "export", request, "shared", progress)
    return dict(motion_file=str(motion_file), bvh_file=exported["bvh_file"],
                fbx_file=exported["fbx_file"], project_dir=request["project_dir"],
                engine=engine, include_shape=include_shape,
                frame_count=captured["frame_count"], fps=captured["motion"]["fps"])
