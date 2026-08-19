"""URL-only, cache-aware YouTube reference intake for Workflow Runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from ...utils.youtube_url import parse_youtube_video_url

_MEDIA_PROFILES = frozenset({"audio_m4a", "video_mp4"})


def _youtube_url(value: Any) -> str:
    if not isinstance(value, str):
        raise InputValidationError("youtube_url")

    try:
        _video_id, canonical_url = parse_youtube_video_url(value)
    except ValueError as error:
        raise InputValidationError("youtube_url") from error
    if not canonical_url:
        raise InputValidationError("youtube_url")
    return canonical_url


def _media_profile(value: Any) -> str:
    if not isinstance(value, str) or value not in _MEDIA_PROFILES:
        raise InputValidationError("media_profile")
    return value


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    """Map the narrow runner input contract onto the downloader node exactly."""

    youtube_url = _youtube_url(inputs.get("youtube_url"))
    media_profile = _media_profile(inputs.get("media_profile"))

    reference = prompt.get("reference")
    if not isinstance(reference, dict) or reference.get("class_type") != "LF_YouTubeReference":
        raise ValueError("youtube reference workflow is missing its reference node")
    reference_inputs = reference.get("inputs")
    if not isinstance(reference_inputs, dict):
        raise ValueError("youtube reference workflow has invalid reference inputs")

    reference_inputs["youtube_url"] = youtube_url
    reference_inputs["media_kind"] = media_profile


input_youtube_url = WorkflowCell(
    node_id="reference",
    id="youtube_url",
    value="YouTube URL",
    shape="textfield",
    description="A YouTube watch, short-link, or mobile URL. The video ID keys the reusable Comfy input cache.",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "url",
            "name": "youtube_url",
            "placeholder": "https://youtu.be/VIDEO_ID",
            "type": "url",
        },
        "lfLabel": "YouTube URL",
    },
)
input_media_profile = WorkflowCell(
    node_id="reference",
    id="media_profile",
    value="Media profile",
    shape="select",
    description="Audio is the light reference path; video preserves the source picture when a later graph needs it.",
    props={
        "lfDataset": {
            "nodes": [
                {"id": "audio_m4a", "value": "Audio (M4A)", "workflowValue": "audio_m4a"},
                {"id": "video_mp4", "value": "Video (MP4)", "workflowValue": "video_mp4"},
            ],
        },
        "lfTextfieldProps": {"lfLabel": "Media profile"},
        "lfValue": "audio_m4a",
    },
)

output_input_reference = WorkflowCell(
    node_id="input_reference",
    id="input_reference",
    shape="code",
    description="Portable Comfy input reference",
)
output_video_id = WorkflowCell(
    node_id="video_id",
    id="video_id",
    shape="code",
    description="Canonical YouTube video ID",
)
output_receipt = WorkflowCell(
    node_id="manifest",
    id="receipt",
    shape="code",
    description="Cached media receipt",
    props={"lfLanguage": "json"},
)

id = "youtube_reference_intake"
node = WorkflowNode(
    id=id,
    value="YouTube Reference Intake",
    description="Download one YouTube reference into Comfy input storage, keyed by video ID and media profile.",
    category="Media Intake",
    inputs=[input_youtube_url, input_media_profile],
    outputs=[output_input_reference, output_video_id, output_receipt],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().with_suffix(".json"),
)
WORKFLOW = node
