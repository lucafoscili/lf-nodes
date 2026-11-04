"""Subprocess boundary for the separately installed RGB MoCap application."""

from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
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
    try:
        revision = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
            encoding="utf-8", errors="replace", check=False,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "RGB MoCap revision check requires git on ComfyUI's PATH. "
            "Install Git or add its executable directory to PATH, then restart ComfyUI."
        ) from error
    if revision.returncode or revision.stdout.strip() != SUPPORTED_COMMIT:
        found = revision.stdout.strip() or "unavailable"
        raise RuntimeError(f"RGB MoCap revision is unsupported at {root}; found {found}; expected {SUPPORTED_COMMIT}.")
    return root


def runtime_python(root, profile):
    path = Path(root) / ("runtime_exmr" if profile == "exmr" else "runtime") / "python.exe"
    if not path.is_file():
        raise RuntimeError(f"RGB MoCap {profile} runtime is missing at {path}. Repair the app installation.")
    return path


def _cuda_preflight(root, gpu_index):
    """Inspect the app's CUDA runtime without importing torch in ComfyUI."""
    environment = os.environ.copy()
    environment.pop("CUDA_VISIBLE_DEVICES", None)
    environment.update(CUDA_DEVICE_ORDER="PCI_BUS_ID", PYTHONDONTWRITEBYTECODE="1")
    probe = (
        "import json, torch; "
        "devices = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] "
        "if torch.cuda.is_available() else []; "
        "print(" + repr(PREFIX) + " + json.dumps(devices))"
    )
    try:
        check = subprocess.run(
            [str(runtime_python(root, "exmr")), "-B", "-I", "-X", "utf8", "-c", probe],
            cwd=str(root), env=environment, capture_output=True, encoding="utf-8",
            errors="replace", timeout=30, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"RGB MoCap CUDA preflight for gpu_index={gpu_index} timed out after 30 seconds; "
            "available devices: unavailable. Check the ExMR runtime and NVIDIA driver."
        ) from error
    devices = None
    for line in check.stdout.splitlines():
        if line.startswith(PREFIX):
            devices = json.loads(line[len(PREFIX):])
    if check.returncode or devices is None:
        detail = (check.stderr or check.stdout).strip()[-2000:]
        raise RuntimeError(
            f"RGB MoCap CUDA preflight failed for gpu_index={gpu_index}; available devices: unavailable. "
            f"Repair the ExMR runtime/NVIDIA driver. {detail}"
        )
    if gpu_index >= len(devices):
        available = ", ".join(f"{index}: {name}" for index, name in enumerate(devices)) or "none"
        raise RuntimeError(
            f"RGB MoCap gpu_index={gpu_index} is unavailable; available CUDA devices "
            f"(PCI_BUS_ID order): {available}. Select a listed index and check the NVIDIA driver."
        )


def _clip_duration(source):
    """Read clip metadata only; inference and preparation still belong to the app."""
    import av

    try:
        with av.open(str(source)) as video:
            stream = video.streams.video[0]
            if stream.duration is not None and stream.time_base is not None:
                duration = float(stream.duration * stream.time_base)
            elif video.duration is not None:
                duration = float(video.duration / av.time_base)
            else:
                duration = float(stream.frames / stream.average_rate)
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError("missing positive finite clip duration")
            return duration
    except Exception as error:
        raise RuntimeError(f"Cannot determine video duration for worker time limits: {source}: {error}") from error


def _stage_timeout(action, request):
    """Bound each worker once; zero selects clip-duration scaling, without retries."""
    override = request.get("stage_timeout_seconds", 0)
    if override:
        return float(override)
    minimum, multiplier = {
        "prepare": (120, 4), "track": (300, 30),
        "capture": (600, 120), "export": (300, 20),
    }[action]
    return max(minimum, multiplier * request["duration_seconds"])


@contextmanager
def _worker_tree(process):
    """Contain app workers and Blender/ffmpeg descendants for the entire stage."""
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        kernel.TerminateJobObject.restype = wintypes.BOOL
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.CloseHandle.restype = wintypes.BOOL
        job = kernel.CreateJobObjectW(None, None)
        if not job or not kernel.AssignProcessToJobObject(job, int(process._handle)):
            error = ctypes.WinError(ctypes.get_last_error())
            if job:
                kernel.CloseHandle(job)
            process.kill()
            process.wait(timeout=5)
            raise RuntimeError(f"Cannot contain RGB MoCap worker process tree: {error}") from error

        def stop():
            if not kernel.TerminateJobObject(job, 1):
                raise ctypes.WinError(ctypes.get_last_error())
    else:
        def stop():
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        if os.name == "nt":
            # Popen closes the primary thread handle, so resume the suspended
            # process only after job assignment using its retained process handle.
            native = ctypes.WinDLL("ntdll")
            native.NtResumeProcess.argtypes = (wintypes.HANDLE,)
            native.NtResumeProcess.restype = wintypes.LONG
            status = native.NtResumeProcess(int(process._handle))
            if status != 0:
                raise RuntimeError(f"Cannot resume contained RGB MoCap worker: NTSTATUS {status:#x}")
        yield stop
    finally:
        active_error = sys.exc_info()[1]
        try:
            stop()
        except OSError as error:
            if active_error is None:
                raise
            if hasattr(active_error, "add_note"):
                active_error.add_note(f"Worker process tree cleanup failed: {error}")
        finally:
            if os.name == "nt":
                kernel.CloseHandle(job)


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
    pending = b""

    def consume(data, final=False):
        nonlocal pending, result, failure
        pending += data
        lines = pending.split(b"\n")
        pending = lines.pop()
        if final and pending:
            lines.append(pending)
            pending = b""
        for raw in lines:
            line = raw.decode("utf-8", errors="replace")
            if not line.startswith(PREFIX):
                continue
            event = json.loads(line[len(PREFIX):])
            if event.get("type") == "result":
                result = event["result"]
            elif event.get("type") == "failed":
                failure = event.get("message", "Worker failed")
            if progress:
                progress(event)

    limit = _stage_timeout(action, request)
    started = time.monotonic()
    # A regular log file cannot block on a silent worker or an inherited pipe.
    with log_path.open("wb") as log, log_path.open("rb") as reader:
        with subprocess.Popen(command, cwd=str(job), env=environment, stdout=log,
                              stderr=subprocess.STDOUT, start_new_session=os.name != "nt",
                              # CREATE_SUSPENDED closes the spawn-before-job race.
                              creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                              | (0x00000004 if os.name == "nt" else 0)) as process:
            with _worker_tree(process) as stop:
                while True:
                    consume(reader.read())
                    code = process.poll()
                    if code is not None:
                        consume(reader.read(), final=True)
                        break
                    elapsed = time.monotonic() - started
                    if elapsed >= limit:
                        stopped = "worker process tree stopped"
                        try:
                            stop()
                            process.wait(timeout=5)
                        except (OSError, subprocess.TimeoutExpired) as error:
                            stopped = f"worker process tree stop failed: {error}"
                            # Keep Popen's exit wait bounded if native tree cleanup fails.
                            try:
                                process.kill()
                                process.wait(timeout=5)
                            except (OSError, subprocess.TimeoutExpired) as fallback_error:
                                stopped += f"; worker fallback stop failed: {fallback_error}"
                        message = (f"RGB MoCap {action} timed out after {elapsed:.2f} seconds "
                                   f"(limit {limit:g} seconds); {stopped}; no retry. "
                                   f"Log: {log_path}")
                        log.write(("\n" + message + "\n").encode("utf-8"))
                        raise RuntimeError(message)
                    time.sleep(min(0.1, limit - elapsed))
    if code or result is None:
        raise RuntimeError(f"RGB MoCap {action} failed: {failure or 'see worker log'}. Log: {log_path}")
    return result


def run_video_to_motion(video_path, output_root, *, engine="ExMR", static_camera=True,
                        smoothing=True, gpu_index=0, include_shape=False, progress=None,
                        stage_timeout_seconds=0.0):
    if engine != "ExMR":
        raise ValueError("engine must be ExMR.")
    if type(gpu_index) is not int or not 0 <= gpu_index <= 31:
        raise ValueError("gpu_index must be an integer from 0 to 31.")
    for name, value in (("static_camera", static_camera), ("smoothing", smoothing),
                        ("include_shape", include_shape)):
        if type(value) is not bool:
            raise ValueError(name + " must be a boolean.")
    if (type(stage_timeout_seconds) not in (int, float)
            or not math.isfinite(stage_timeout_seconds) or stage_timeout_seconds < 0):
        raise ValueError("stage_timeout_seconds must be a finite nonnegative number; 0 selects automatic limits.")
    source = Path(video_path).expanduser().resolve()
    if not source.is_file():
        raise ValueError("video_path must name an existing local video file.")
    root = installation_path()
    runtime_python(root, "exmr")
    runtime_python(root, "shared")
    _cuda_preflight(root, gpu_index)
    duration = _clip_duration(source)
    output_root = Path(output_root).resolve()
    job = output_root / "LF_Nodes" / "Motion" / ("capture_" + uuid.uuid4().hex[:12])
    if not job.resolve().is_relative_to(output_root):
        raise ValueError("Motion output directory escapes ComfyUI output.")
    job.mkdir(parents=True)
    request = dict(video_path=str(source), static_camera=static_camera,
                   smoothing=smoothing, gpu_index=gpu_index, include_shape=include_shape,
                   joint_names=JOINT_NAMES, duration_seconds=duration,
                   stage_timeout_seconds=stage_timeout_seconds)
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
