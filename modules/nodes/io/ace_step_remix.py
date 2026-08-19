"""Opt-in HTTP bridge for ACE-Step audio cover and repaint jobs.

The node deliberately keeps the model server outside ComfyUI.  The only
filesystem input accepted is a file inside one of ComfyUI's managed media
roots, and the server result is copied back into ComfyUI's output directory.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import time
import uuid

from pathlib import Path
from urllib.parse import urljoin, urlparse

import folder_paths
import requests

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.env import bool_env


_DEFAULT_API_URL = "http://127.0.0.1:8001"
_REQUEST_TIMEOUT = (10, 30)
_DEFAULT_POLL_TIMEOUT_SECONDS = 60 * 60
_MAX_POLL_TIMEOUT_SECONDS = 24 * 60 * 60
_POLL_INTERVAL_SECONDS = 0.5
_MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024
_HTTP = requests
_SLEEP = time.sleep
_OUTPUT_FORMATS = ("mp3", "wav", "flac")
_MODES = ("cover", "repaint")
_INFER_METHODS = ("ode", "sde")


def _normalized(path: Path) -> Path:
    """Resolve a path without allowing a missing path to evade containment."""

    try:
        return path.expanduser().resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError("Source audio does not exist") from error


def _contained(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _managed_roots() -> dict[str, Path]:
    return {
        "input": _normalized(Path(folder_paths.get_input_directory())),
        "temp": _normalized(Path(folder_paths.get_temp_directory())),
        "output": _normalized(Path(folder_paths.get_output_directory())),
    }


def _raw_source(value) -> str:
    """Accept the string produced by the upload cell and common Comfy wrappers."""

    while isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError("Source audio must identify exactly one file")
        value = value[0]
    if isinstance(value, dict):
        for key in ("path", "filename", "file", "value"):
            if key in value:
                return _raw_source(value[key])
        raise ValueError("Source audio upload has no portable path")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Source audio is required")
    return value.strip()


def _resolve_source_path(value) -> tuple[Path, str, str]:
    """Return ``(resolved_path, managed_root_name, portable_reference)``.

    Unannotated relative paths are looked up in input, temp, and output roots;
    an explicit ``[input]``/``[temp]``/``[output]`` suffix or prefix removes
    ambiguity.  Symlink targets are resolved before containment is checked.
    """

    raw = _raw_source(value)
    root_name = None
    for suffix in ("input", "temp", "output"):
        marker = f" [{suffix}]"
        if raw.lower().endswith(marker):
            raw = raw[: -len(marker)].strip()
            root_name = suffix
            break

    raw_path = Path(raw)
    if not raw_path.is_absolute():
        parts = raw_path.parts
        if parts and parts[0].lower() in ("input", "temp", "output"):
            root_name = parts[0].lower()
            raw_path = Path(*parts[1:])

    roots = _managed_roots()
    candidates: list[tuple[str, Path]] = []
    if raw_path.is_absolute():
        resolved = _normalized(raw_path)
        candidates = [(name, resolved) for name, root in roots.items() if _contained(root, resolved)]
    elif root_name is not None:
        candidate = _normalized(roots[root_name] / raw_path)
        candidates = [(root_name, candidate)] if _contained(roots[root_name], candidate) else []
    else:
        for name, root in roots.items():
            candidate = root / raw_path
            try:
                resolved = _normalized(candidate)
            except ValueError:
                continue
            if _contained(root, resolved):
                candidates.append((name, resolved))

    unique = {(name, path) for name, path in candidates}
    if len(unique) != 1:
        raise ValueError("Source audio must be a file inside ComfyUI input, temp, or output")
    root_name, source_path = next(iter(unique))
    if not source_path.is_file() or source_path.is_symlink():
        raise ValueError("Source audio must be a regular file")
    relative = source_path.relative_to(roots[root_name]).as_posix()
    return source_path, root_name, f"{relative} [{root_name}]"


def _float_control(name: str, value, minimum: float, maximum: float) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a number") from error
    if not minimum <= number <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return number


def _int_control(name: str, value, minimum: int, maximum: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer") from error
    if number < minimum or number > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return number


def _controls(mode, style_prompt, lyrics, instrumental, audio_cover_strength,
              cover_noise_strength, repaint_start, repaint_end, seed,
              inference_steps, guidance_scale, infer_method, shift,
              output_format) -> dict:
    if mode not in _MODES:
        raise ValueError("mode must be cover or repaint")
    if not isinstance(style_prompt, str) or not isinstance(lyrics, str):
        raise ValueError("style_prompt and lyrics must be strings")
    if not isinstance(instrumental, bool):
        raise ValueError("instrumental must be a boolean")
    controls = {
        "audio_cover_strength": _float_control("audio_cover_strength", audio_cover_strength, 0.0, 1.0),
        "cover_noise_strength": _float_control("cover_noise_strength", cover_noise_strength, 0.0, 1.0),
        "repaint_start": _float_control("repaint_start", repaint_start, 0.0, 24 * 60 * 60),
        "repaint_end": _float_control("repaint_end", repaint_end, -1.0, 24 * 60 * 60),
        "seed": _int_control("seed", seed, -1, 0x7FFFFFFFFFFFFFFF),
        "inference_steps": _int_control("inference_steps", inference_steps, 1, 200),
        "guidance_scale": _float_control("guidance_scale", guidance_scale, 0.0, 100.0),
        "shift": _float_control("shift", shift, 1.0, 5.0),
    }
    if controls["repaint_end"] >= 0 and controls["repaint_end"] < controls["repaint_start"]:
        raise ValueError("repaint_end must be after repaint_start")
    if output_format not in _OUTPUT_FORMATS:
        raise ValueError("output_format must be mp3, wav, or flac")
    if infer_method not in _INFER_METHODS:
        raise ValueError("infer_method must be ode or sde")
    controls.update({
        "mode": mode,
        "style_prompt": style_prompt.strip(),
        "lyrics": lyrics,
        "instrumental": instrumental,
        "infer_method": infer_method,
        "output_format": output_format,
    })
    return controls


def _api_url() -> str:
    value = os.environ.get("LF_ACESTEP_API_URL", _DEFAULT_API_URL).strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("LF_ACESTEP_API_URL must be an HTTP(S) URL without credentials")
    return value


def _headers() -> dict[str, str]:
    token = os.environ.get("LF_ACESTEP_API_TOKEN", "").strip()
    return {"Authorization": f"Bearer {token}"} if token else {}


def _poll_timeout_seconds() -> int:
    raw = os.environ.get(
        "LF_ACESTEP_TIMEOUT_SECONDS",
        str(_DEFAULT_POLL_TIMEOUT_SECONDS),
    ).strip()
    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError("LF_ACESTEP_TIMEOUT_SECONDS must be an integer") from error
    if value < 1 or value > _MAX_POLL_TIMEOUT_SECONDS:
        raise ValueError(
            "LF_ACESTEP_TIMEOUT_SECONDS must be between 1 and 86400"
        )
    return value


def _json_response(response, label: str):
    try:
        response.raise_for_status()
        value = response.json()
    except (requests.RequestException, ValueError, json.JSONDecodeError) as error:
        raise RuntimeError(f"ACE-Step {label} response was invalid") from error
    return value


def _task_id(payload) -> str:
    value = payload.get("data", payload) if isinstance(payload, dict) else payload
    if isinstance(value, dict):
        value = value.get("task_id") or value.get("taskId") or value.get("id")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("ACE-Step did not return a task id")
    return value.strip()


def _result_row(payload):
    value = payload.get("data", payload) if isinstance(payload, dict) else payload
    if isinstance(value, dict):
        rows = [value]
    elif isinstance(value, list):
        rows = value
    else:
        raise RuntimeError("ACE-Step query response had no task result")
    if not rows or not isinstance(rows[0], dict):
        raise RuntimeError("ACE-Step query response had no task result")
    return rows[0]


def _result_reference(row) -> str:
    value = row.get("result", row.get("output", row.get("audio")))
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return value
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, dict):
        value = value.get("file") or value.get("path") or value.get("url") or value.get("audio")
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError("ACE-Step result did not contain an audio file")
    return value.strip()


def _result_url(base: str, reference: str) -> str:
    parsed = urlparse(reference)
    base_parsed = urlparse(base)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != base_parsed.scheme or parsed.netloc != base_parsed.netloc:
            raise RuntimeError("ACE-Step result URL points to a different host")
        return reference
    if not reference.startswith("/"):
        raise RuntimeError("ACE-Step result must be an absolute API path or same-host URL")
    return urljoin(base + "/", reference)


def _download(base: str, reference: str, output_format: str) -> tuple[Path, int, str]:
    output_root = _normalized(Path(folder_paths.get_output_directory()))
    destination_dir = output_root / "lf-workflow-runner" / "ace-step"
    destination_dir.mkdir(parents=True, exist_ok=True)
    if not _contained(output_root, destination_dir):
        raise RuntimeError("ACE-Step output directory escaped ComfyUI output")
    destination = destination_dir / f"{uuid.uuid4().hex}.{output_format}"
    partial = destination.with_suffix(destination.suffix + ".part")
    total = 0
    digest = hashlib.sha256()
    try:
        response = _HTTP.get(_result_url(base, reference), headers=_headers(), stream=True, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        content_length = response.headers.get("Content-Length")
        if content_length is not None and int(content_length) > _MAX_DOWNLOAD_BYTES:
            raise RuntimeError("ACE-Step output exceeds the download limit")
        with partial.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > _MAX_DOWNLOAD_BYTES:
                    raise RuntimeError("ACE-Step output exceeds the download limit")
                digest.update(chunk)
                handle.write(chunk)
        if total <= 0:
            raise RuntimeError("ACE-Step returned an empty audio file")
        os.replace(partial, destination)
    except Exception:
        try:
            partial.unlink()
        except FileNotFoundError:
            pass
        raise
    return destination, total, digest.hexdigest()


def _poll(base: str, task_id: str):
    deadline = time.monotonic() + _poll_timeout_seconds()
    while time.monotonic() < deadline:
        response = _HTTP.post(
            f"{base}/query_result",
            json={"task_id_list": [task_id]},
            headers=_headers(),
            timeout=_REQUEST_TIMEOUT,
        )
        row = _result_row(_json_response(response, "query"))
        status = row.get("status")
        if status in (1, "1", "success", "completed", "succeeded"):
            return row
        if status in (2, "2", "failed", "error", "cancelled"):
            raise RuntimeError(str(
                row.get("error")
                or row.get("message")
                or row.get("progress_text")
                or "ACE-Step task failed"
            ))
        if status not in (0, "0", "queued", "processing", "running", "pending"):
            raise RuntimeError("ACE-Step returned an unknown task status")
        _SLEEP(_POLL_INTERVAL_SECONDS)
    raise TimeoutError("Timed out waiting for ACE-Step task")


class LF_ACEStepRemix:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source_audio": (Input.STRING, {"default": ""}),
                "mode": (list(_MODES), {"default": "cover"}),
                "style_prompt": (Input.STRING, {"default": "", "multiline": True}),
                "lyrics": (Input.STRING, {"default": "", "multiline": True}),
                "instrumental": (Input.BOOLEAN, {"default": False}),
                "audio_cover_strength": (Input.FLOAT, {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "cover_noise_strength": (Input.FLOAT, {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.01}),
                "repaint_start": (Input.FLOAT, {"default": 0.0, "min": 0.0, "max": 86400.0, "step": 0.1}),
                "repaint_end": (Input.FLOAT, {"default": -1.0, "min": -1.0, "max": 86400.0, "step": 0.1}),
                "seed": (Input.INTEGER, {"default": -1, "min": -1, "max": 0x7FFFFFFFFFFFFFFF}),
                "inference_steps": (Input.INTEGER, {"default": 8, "min": 1, "max": 200}),
                "guidance_scale": (Input.FLOAT, {"default": 7.0, "min": 0.0, "max": 100.0, "step": 0.1}),
                "infer_method": (list(_INFER_METHODS), {"default": "ode"}),
                "shift": (Input.FLOAT, {"default": 3.0, "min": 1.0, "max": 5.0, "step": 0.1}),
                # FLAC is lossless and uses ACE-Step's built-in soundfile path.
                # MP3 remains available but requires ffmpeg in the API runtime.
                "output_format": (list(_OUTPUT_FORMATS), {"default": "flac"}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.STRING, Input.JSON)
    RETURN_NAMES = ("output_reference", "receipt")
    OUTPUT_TOOLTIPS = (
        "Portable path below ComfyUI output; a playable audio artifact is also returned in the UI.",
        "JSON receipt for the submitted job and downloaded output.",
    )

    def on_exec(self, source_audio, mode, style_prompt, lyrics, instrumental,
                audio_cover_strength, cover_noise_strength, repaint_start,
                repaint_end, seed, inference_steps, guidance_scale,
                infer_method, shift, output_format, **kwargs):
        if not bool_env("LF_ACESTEP_ENABLED", False):
            raise RuntimeError("ACE-Step remix is disabled; set LF_ACESTEP_ENABLED=1 to enable it")
        source_path, source_root, source_reference = _resolve_source_path(source_audio)
        controls = _controls(mode, style_prompt, lyrics, instrumental, audio_cover_strength,
                             cover_noise_strength, repaint_start, repaint_end, seed,
                             inference_steps, guidance_scale, infer_method, shift,
                             output_format)
        base = _api_url()
        data = {
            "task_type": controls["mode"],
            "prompt": controls["style_prompt"],
            "caption": controls["style_prompt"],
            "lyrics": "[Instrumental]" if controls["instrumental"] else controls["lyrics"],
            "audio_cover_strength": str(controls["audio_cover_strength"]),
            "cover_noise_strength": str(controls["cover_noise_strength"]),
            "repainting_start": str(controls["repaint_start"]),
            "repainting_end": str(controls["repaint_end"]),
            "seed": str(controls["seed"]),
            "use_random_seed": "true" if controls["seed"] == -1 else "false",
            "inference_steps": str(controls["inference_steps"]),
            "guidance_scale": str(controls["guidance_scale"]),
            "infer_method": controls["infer_method"],
            "shift": str(controls["shift"]),
            "audio_format": controls["output_format"],
            # This bridge returns one typed output.  ACE-Step's HTTP API
            # otherwise defaults to two generations, wasting VRAM and leaving
            # the second artifact unrepresented in the workflow result.
            "batch_size": "1",
        }
        content_type = mimetypes.guess_type(source_path.name)[0] or "application/octet-stream"
        with source_path.open("rb") as handle:
            response = _HTTP.post(
                f"{base}/release_task",
                data=data,
                files={"src_audio": (source_path.name, handle, content_type)},
                headers=_headers(),
                timeout=_REQUEST_TIMEOUT,
            )
        task_id = _task_id(_json_response(response, "release"))
        row = _poll(base, task_id)
        output_path, output_bytes, output_sha256 = _download(base, _result_reference(row), controls["output_format"])
        output_root = _normalized(Path(folder_paths.get_output_directory()))
        relative = output_path.relative_to(output_root).as_posix()
        output_reference = f"{relative} [output]"
        receipt = {
            "schema": "lf.ace-step-remix.v1",
            "status": "completed",
            "task_id": task_id,
            "source_reference": source_reference,
            "source_root": source_root,
            "controls": controls,
            "output_reference": output_reference,
            "bytes": output_bytes,
            "sha256": output_sha256,
        }
        ui = {"audio": [{"filename": output_path.name, "subfolder": output_path.parent.relative_to(output_root).as_posix(), "type": "output"}]}
        return {"ui": ui, "result": (output_reference, receipt)}


NODE_CLASS_MAPPINGS = {"LF_ACEStepRemix": LF_ACEStepRemix}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_ACEStepRemix": "ACE-Step Remix (opt-in)"}
