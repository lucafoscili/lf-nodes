"""Extract generic motion, then inspect it on an independently chosen body."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from ..services.registry import (
    InputValidationError,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowNode,
)
from .utils import choice, integer, resolve_upload_paths


def _configure(prompt: dict[str, Any], inputs: dict[str, Any], *, resolve_upload: bool) -> None:
    # Imported per run: catalogue declarations load without the node helper package.
    from ...utils.helpers.motion.render import parse_betas
    from ...utils.helpers.motion.rgb_mocap import planted_spans

    engine = choice(inputs, "engine", "ExMR", ("ExMR",))
    body = choice(inputs, "body", "female", ("female", "neutral", "male"))
    betas = inputs.get("betas", "0.5,-1.5")
    try:
        parse_betas(betas)
    except ValueError as error:
        raise InputValidationError("betas") from error
    static_camera = inputs.get("static_camera", True)
    smoothing = inputs.get("smoothing", True)
    include_shape = inputs.get("include_shape", False)
    motion_correction = inputs.get("motion_correction", True)
    ground_feet = inputs.get("ground_feet", True)
    for name, value in (("static_camera", static_camera), ("smoothing", smoothing),
                        ("include_shape", include_shape), ("motion_correction", motion_correction),
                        ("ground_feet", ground_feet)):
        if not isinstance(value, bool):
            raise InputValidationError(name)
    push_in = choice(inputs, "push_in", "auto", ("auto", "yes", "no"))
    planted_seconds = inputs.get("planted_seconds", "") or ""
    try:
        if not isinstance(planted_seconds, str) or (planted_spans(planted_seconds)
                                                    and not (motion_correction and ground_feet)):
            raise ValueError(planted_seconds)
    except ValueError as error:
        raise InputValidationError("planted_seconds") from error
    timeout = inputs.get("stage_timeout_seconds", 0.0)
    if timeout in (None, ""):
        timeout = 0.0
    if isinstance(timeout, bool):
        raise InputValidationError("stage_timeout_seconds")
    try:
        timeout = float(timeout)
    except (TypeError, ValueError) as error:
        raise InputValidationError("stage_timeout_seconds") from error
    if not math.isfinite(timeout) or not 0.0 <= timeout <= 86400.0:
        raise InputValidationError("stage_timeout_seconds")
    gpu_index = integer(inputs, "gpu_index", 0, minimum=0, maximum=31)
    width = integer(inputs, "width", 320, minimum=64, maximum=2048)
    height = integer(inputs, "height", 560, minimum=64, maximum=2048)
    for name, value in (("width", width), ("height", height)):
        if value % 2:
            raise InputValidationError(name)
    video_path = "video.mp4"
    if resolve_upload:
        paths = resolve_upload_paths(inputs, "video_path", allow_multiple=True)
        if len(paths) != 1 or not Path(paths[0]).is_file():
            raise InputValidationError("video_path")
        video_path = paths[0]
    target_fields = ("glb_path", "bone_map_path")
    supplied = {name: inputs.get(name) not in (None, "", []) for name in target_fields}
    if any(supplied.values()) and not all(supplied.values()):
        raise InputValidationError(next(name for name in target_fields if not supplied[name]))
    target_paths = {}
    if all(supplied.values()):
        for name, suffix, portable in (("glb_path", ".glb", "target.glb"),
                                       ("bone_map_path", ".json", "bone-map.json")):
            paths = resolve_upload_paths(inputs, name, allow_multiple=True, must_exist=resolve_upload)
            if (len(paths) != 1 or Path(paths[0]).suffix.lower() != suffix
                    or (resolve_upload and not Path(paths[0]).is_file())):
                raise InputValidationError(name)
            target_paths[name] = paths[0] if resolve_upload else portable
    prompt["extract_motion"]["inputs"].update(
        video_path=video_path, engine=engine, static_camera=static_camera,
        smoothing=smoothing, gpu_index=gpu_index, include_shape=include_shape,
        stage_timeout_seconds=timeout, motion_correction=motion_correction,
        ground_feet=ground_feet, push_in=push_in, planted_seconds=planted_seconds,
    )
    prompt["render_motion"]["inputs"].update(
        body=body, betas=betas, width=width, height=height, source_video=video_path,
    )
    if target_paths:
        prompt["retarget_motion"] = {
            "class_type": "LF_RetargetMotion",
            "inputs": {"motion_file": ["extract_motion", 0], "body": body, "betas": betas,
                       **target_paths, "keep_rest_facing": "[]", "flatten_slope": "[]"},
            "_meta": {"title": "Retarget motion onto the uploaded rig"},
        }
        prompt["render_motion"]["inputs"]["body_glb"] = ["retarget_motion", 0]


def _configure_run(prompt: dict[str, Any], inputs: dict[str, Any]) -> None:
    _configure(prompt, inputs, resolve_upload=True)


def _configure_download(prompt: dict[str, Any], inputs: dict[str, Any]) -> None:
    _configure(prompt, inputs, resolve_upload=False)


def _number(name: str, node_id: str, label: str, default: int, minimum: int, maximum: int) -> WorkflowCell:
    return WorkflowCell(
        id=name, node_id=node_id, shape="textfield", required=False,
        description=label,
        props={"lfLabel": label, "lfValue": str(default), "lfHtmlAttributes": {
            "name": name, "type": "number", "min": minimum, "max": maximum,
            "step": 2 if name in ("width", "height") else 1,
        }},
    )


WORKFLOW = WorkflowNode(
    id="video_to_mocap",
    value="Video to Motion Capture",
    category="Motion",
    description=(
        "Extract body and hand motion from one video with a configured local RGB-Mocap ExMR runtime, "
        "ground it with the app's Motion Correction, then render a source comparison on a separately "
        "chosen SMPL-X body. "
        "Requires RGB_MOCAP_PATH and licensed SMPL-X model files; no runtime or model downloads are started."
    ),
    card=WorkflowCardPresentation(summary="Extract motion and inspect it on a body you choose."),
    inputs=(
        WorkflowCell(
            id="video_path", node_id="extract_motion", shape="upload",
            value="Source video", description="One video with a clearly visible performer.",
            props={"lfLabel": "Source video", "lfHtmlAttributes": {"accept": "video/*"}},
        ),
        WorkflowCell(
            id="body", node_id="render_motion", shape="select", required=False,
            description="Render body model; independent of the performer shape.",
            props={"lfValue": "female", "lfTextfieldProps": {"lfLabel": "Render body"},
                   "lfDataset": {"nodes": [{"id": body, "value": body.title(), "workflowValue": body}
                                            for body in ("female", "neutral", "male")]}},
        ),
        WorkflowCell(
            id="betas", node_id="render_motion", shape="textfield", required=False,
            description="Comma-separated SMPL-X shape coefficients for the render body.",
            props={"lfLabel": "Render shape", "lfValue": "0.5,-1.5"},
        ),
        WorkflowCell(
            id="glb_path", node_id="retarget_motion", shape="upload", required=False,
            value="Target rig", description="Optional rigged GLB; also upload its bone map.",
            props={"lfLabel": "Target rig (optional)", "lfHtmlAttributes": {"accept": ".glb"}},
        ),
        WorkflowCell(
            id="bone_map_path", node_id="retarget_motion", shape="upload", required=False,
            value="Bone map", description="Explicit SMPL-X to target bone map JSON for the target rig.",
            props={"lfLabel": "Bone map (with target rig)", "lfHtmlAttributes": {"accept": ".json"}},
        ),
        _number("width", "render_motion", "Render width", 320, 64, 2048),
        _number("height", "render_motion", "Render height", 560, 64, 2048),
        WorkflowCell(
            id="engine", node_id="extract_motion", shape="select", required=False,
            description="Installed motion extraction engine.",
            props={"lfValue": "ExMR", "lfTextfieldProps": {"lfLabel": "Capture engine"},
                   "lfDataset": {"nodes": [{"id": "ExMR", "value": "ExMR", "workflowValue": "ExMR"}]}},
        ),
        WorkflowCell(
            id="static_camera", node_id="extract_motion", shape="toggle", required=False,
            description="Enable when the source camera is fixed.",
            props={"lfLabel": "Static camera", "lfValue": True},
        ),
        WorkflowCell(
            id="smoothing", node_id="extract_motion", shape="toggle", required=False,
            description="Smooth the extracted motion.",
            props={"lfLabel": "Smooth motion", "lfValue": True},
        ),
        _number("gpu_index", "extract_motion", "Extraction GPU", 0, 0, 31),
        WorkflowCell(
            id="include_shape", node_id="extract_motion", shape="toggle", required=False,
            description="Include inferred performer shape in motion JSON and BVH/FBX exports.",
            props={"lfLabel": "Include performer shape", "lfValue": False},
        ),
        WorkflowCell(
            id="motion_correction", node_id="extract_motion", shape="toggle", required=False,
            description="Ground the motion with RGB MoCap's Motion Correction: one floor, each standing foot held on it.",
            props={"lfLabel": "Motion correction", "lfValue": True},
        ),
        _number("stage_timeout_seconds", "extract_motion", "Stage timeout (seconds; 0 = automatic)", 0, 0, 86400),
        WorkflowCell(
            id="ground_feet", node_id="extract_motion", shape="toggle", required=False,
            description=("With Motion correction: take the camera's drift out of the motion, keep the pelvis over "
                         "the feet when the camera pushes in, and set a standing foot resting on its heel flat."),
            props={"lfLabel": "Ground the feet", "lfValue": True},
        ),
        WorkflowCell(
            id="push_in", node_id="extract_motion", shape="select", required=False,
            description="Whether the camera pushes in or pulls out; auto reads it from the motion.",
            props={"lfValue": "auto", "lfTextfieldProps": {"lfLabel": "Camera push-in"},
                   "lfDataset": {"nodes": [{"id": value, "value": value.title(), "workflowValue": value}
                                            for value in ("auto", "yes", "no")]}},
        ),
        WorkflowCell(
            id="planted_seconds", node_id="extract_motion", shape="textfield", required=False,
            description="Seconds where both feet stay planted, as spans such as 1.65-2.3, 4-5.",
            props={"lfLabel": "Planted seconds", "lfValue": ""},
        ),
    ),
    outputs=(
        WorkflowCell(
            id="comparison", node_id="render_motion", shape="code",
            description="Saved source/comparison video and render details.", props={"lfLanguage": "json"},
        ),
        WorkflowCell(
            id="motion", node_id="extract_motion", shape="code",
            description="Generic motion JSON, BVH and FBX downloads plus extraction details.",
            props={"lfLanguage": "json"},
        ),
    ),
    configure_prompt=_configure_run,
    configure_download=_configure_download,
    workflow_path=Path(__file__).with_suffix(".json"),
)
