"""Extract generic motion, then inspect it on an independently chosen body."""

from __future__ import annotations

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

    body = choice(inputs, "body", "female", ("female", "neutral", "male"))
    betas = inputs.get("betas", "0.5,-1.5")
    try:
        parse_betas(betas)
    except ValueError as error:
        raise InputValidationError("betas") from error
    static_camera = inputs.get("static_camera", True)
    smoothing = inputs.get("smoothing", True)
    for name, value in (("static_camera", static_camera), ("smoothing", smoothing)):
        if not isinstance(value, bool):
            raise InputValidationError(name)
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
    prompt["extract_motion"]["inputs"].update(
        video_path=video_path, static_camera=static_camera, smoothing=smoothing, gpu_index=gpu_index,
    )
    prompt["render_motion"]["inputs"].update(
        body=body, betas=betas, width=width, height=height, source_video=video_path,
    )


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
        "then render a source comparison on a separately chosen SMPL-X body. "
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
        _number("width", "render_motion", "Render width", 320, 64, 2048),
        _number("height", "render_motion", "Render height", 560, 64, 2048),
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
