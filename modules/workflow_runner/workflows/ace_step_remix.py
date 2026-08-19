"""Packaged Workflow Runner graph for the generic ACE-Step remix node."""

from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode


_MODES = ("cover", "repaint")
_FORMATS = ("mp3", "wav", "flac")
_INFER_METHODS = ("ode", "sde")


def _required_text(inputs: Dict[str, Any], name: str) -> str:
    value = inputs.get(name)
    if not isinstance(value, str) or not value.strip():
        raise InputValidationError(name)
    return value.strip()


def _number(inputs: Dict[str, Any], name: str, default, minimum, maximum, integer=False):
    value = inputs.get(name, default)
    if isinstance(value, bool):
        raise InputValidationError(name)
    try:
        value = int(value) if integer else float(value)
    except (TypeError, ValueError):
        raise InputValidationError(name)
    if value < minimum or value > maximum:
        raise InputValidationError(name)
    return value


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    source_audio = _required_text(inputs, "source_audio")
    mode = inputs.get("mode", "cover")
    if mode not in _MODES:
        raise InputValidationError("mode")
    style_prompt = inputs.get("style_prompt", "")
    lyrics = inputs.get("lyrics", "")
    if not isinstance(style_prompt, str) or not isinstance(lyrics, str):
        raise InputValidationError("style_prompt" if not isinstance(style_prompt, str) else "lyrics")
    instrumental = inputs.get("instrumental", False)
    if not isinstance(instrumental, bool):
        raise InputValidationError("instrumental")
    audio_cover_strength = _number(inputs, "audio_cover_strength", 1.0, 0.0, 1.0)
    cover_noise_strength = _number(inputs, "cover_noise_strength", 0.2, 0.0, 1.0)
    repaint_start = _number(inputs, "repaint_start", 0.0, 0.0, 86400.0)
    repaint_end = _number(inputs, "repaint_end", -1.0, -1.0, 86400.0)
    if repaint_end >= 0 and repaint_end < repaint_start:
        raise InputValidationError("repaint_end")
    seed = _number(inputs, "seed", -1, -1, 0x7FFFFFFFFFFFFFFF, integer=True)
    inference_steps = _number(inputs, "inference_steps", 8, 1, 200, integer=True)
    guidance_scale = _number(inputs, "guidance_scale", 7.0, 0.0, 100.0)
    infer_method = inputs.get("infer_method", "ode")
    if infer_method not in _INFER_METHODS:
        raise InputValidationError("infer_method")
    shift = _number(inputs, "shift", 3.0, 1.0, 5.0)
    output_format = inputs.get("output_format", "mp3")
    if output_format not in _FORMATS:
        raise InputValidationError("output_format")

    remix = prompt.get("remix")
    if not isinstance(remix, dict) or remix.get("class_type") != "LF_ACEStepRemix":
        raise ValueError("ACE-Step remix workflow is missing its remix node")
    remix_inputs = remix.get("inputs")
    if not isinstance(remix_inputs, dict):
        raise ValueError("ACE-Step remix workflow has invalid remix inputs")

    remix_inputs.update({
        "source_audio": source_audio,
        "mode": mode,
        "style_prompt": style_prompt,
        "lyrics": lyrics,
        "instrumental": instrumental,
        "audio_cover_strength": audio_cover_strength,
        "cover_noise_strength": cover_noise_strength,
        "repaint_start": repaint_start,
        "repaint_end": repaint_end,
        "seed": seed,
        "inference_steps": inference_steps,
        "guidance_scale": guidance_scale,
        "infer_method": infer_method,
        "shift": shift,
        "output_format": output_format,
    })


_source_audio = WorkflowCell(
    node_id="remix",
    id="source_audio",
    shape="upload",
    props={
        "lfLabel": "Source audio",
        "lfHtmlAttributes": {"accept": "audio/*", "multiple": False},
    },
)
_mode = WorkflowCell(
    node_id="remix", id="mode", shape="select", value="Mode",
    props={"lfLabel": "Mode", "lfOptions": [
        {"label": "Cover", "value": "cover"},
        {"label": "Repaint", "value": "repaint"},
    ], "lfValue": "cover"},
)


def _text_cell(cell_id: str, label: str, helper: str, required: bool = False) -> WorkflowCell:
    return WorkflowCell(
        node_id="remix", id=cell_id, shape="textfield", required=required,
        props={"lfLabel": label, "lfHelper": {"showWhenFocused": False, "value": helper}, "lfStyling": "textarea"},
    )


def _number_cell(cell_id: str, label: str, default, minimum, maximum, step) -> WorkflowCell:
    return WorkflowCell(
        node_id="remix", id=cell_id, shape="textfield", props={
            "lfLabel": label,
            "lfHtmlAttributes": {"name": cell_id, "type": "number", "min": minimum, "max": maximum, "step": step},
            "lfValue": str(default),
        },
    )


id = "ace_step_remix"
node = WorkflowNode(
    id=id,
    value="ACE-Step Audio Remix",
    description="Cover or repaint a ComfyUI audio upload through a configured ACE-Step API.",
    category="Audio",
    inputs=[
        _source_audio,
        _mode,
        _text_cell("style_prompt", "Style prompt", "Optional genre, mood, instrumentation, and production direction."),
        _text_cell("lyrics", "Lyrics", "Optional lyrics. The Instrumental toggle overrides this field."),
        WorkflowCell(node_id="remix", id="instrumental", shape="toggle", props={"lfLabel": "Instrumental", "lfValue": False}, required=False),
        _number_cell("audio_cover_strength", "Structure strength", 1.0, 0.0, 1.0, 0.01),
        _number_cell("cover_noise_strength", "Melody retention", 0.2, 0.0, 1.0, 0.01),
        _number_cell("repaint_start", "Repaint start (seconds)", 0.0, 0.0, 86400.0, 0.1),
        _number_cell("repaint_end", "Repaint end (seconds)", -1.0, -1.0, 86400.0, 0.1),
        _number_cell("seed", "Seed", -1, -1, 0x7FFFFFFFFFFFFFFF, 1),
        _number_cell("inference_steps", "Steps", 8, 1, 200, 1),
        _number_cell("guidance_scale", "Guidance", 7.0, 0.0, 100.0, 0.1),
        WorkflowCell(node_id="remix", id="infer_method", shape="select", value="Sampler", props={"lfLabel": "Sampler", "lfOptions": [
            {"label": "ODE", "value": "ode"},
            {"label": "SDE", "value": "sde"},
        ], "lfValue": "ode"}),
        _number_cell("shift", "Timestep shift", 3.0, 1.0, 5.0, 0.1),
        WorkflowCell(node_id="remix", id="output_format", shape="select", value="Output format", props={"lfLabel": "Output format", "lfOptions": [
            {"label": value.upper(), "value": value} for value in _FORMATS
        ], "lfValue": "mp3"}),
    ],
    outputs=[
        WorkflowCell(node_id="remix", id="audio", shape="masonry", description="Generated audio."),
        WorkflowCell(node_id="output_reference", id="output_reference", shape="code", description="Portable ComfyUI output reference."),
        WorkflowCell(node_id="receipt", id="receipt", shape="code", description="ACE-Step job and output receipt.", props={"lfLanguage": "json"}),
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
)

WORKFLOW = node
