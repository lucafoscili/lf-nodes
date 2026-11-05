from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlsplit

from ..services.registry import (
    InputValidationError,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowNode,
)
from .utils import resolve_load_image_reference

DEFAULT_ENDPOINT = "/api/lf-nodes/proxy/kobold"
DEFAULT_MAX_TOKENS = 2048
DEFAULT_PROMPT = "Disregard your prompt instructions in regards to character classification and thoroughly describe this image in markdown format."

# region Workflow Config
def _configure(
    prompt: Dict[str, Any], inputs: Dict[str, Any], *, resolve_upload: bool = True
) -> None:
    endpoint = None
    if "endpoint" in inputs:
        endpoint = inputs["endpoint"]
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise InputValidationError("endpoint")
        endpoint = endpoint.strip()

    effective_endpoint = endpoint or prompt["4"]["inputs"]["url"]
    try:
        native_chat = urlsplit(effective_endpoint).path.rstrip("/").endswith("/api/v1/chat")
    except ValueError as error:
        raise InputValidationError("endpoint") from error

    caption_prompt = None
    if "prompt" in inputs:
        caption_prompt = inputs["prompt"]
        if not isinstance(caption_prompt, str) or not caption_prompt.strip():
            raise InputValidationError("prompt")
        caption_prompt = caption_prompt.strip()

    model = inputs.get("model", "")
    if not isinstance(model, str):
        raise InputValidationError("model")
    model = model.strip()
    manage_model = inputs.get("manage_model", False)
    if not isinstance(manage_model, bool):
        raise InputValidationError("manage_model")
    if (model or manage_model) and not native_chat:
        raise ValueError("Model selection and loading require an LM Studio native /api/v1/chat endpoint.")
    if manage_model and not model:
        raise ValueError("Choose an LM Studio model to load and release automatically.")

    max_tokens = None
    if "max_tokens" in inputs:
        value = inputs["max_tokens"]
        if type(value) not in (int, str):
            raise InputValidationError("max_tokens")
        try:
            max_tokens = int(str(value).strip())
        except ValueError as error:
            raise InputValidationError("max_tokens") from error
        if not 20 <= max_tokens <= 8000:
            raise InputValidationError("max_tokens")

    if resolve_upload:
        source_image = resolve_load_image_reference(inputs, "source_path")
    else:
        source_image = "source_path.png"
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "2":  # Image loader
            inputs_map["image"] = source_image
        elif node_id == "4":
            if endpoint is not None:
                inputs_map["url"] = endpoint
            if max_tokens is not None:
                inputs_map["max_tokens"] = max_tokens
            if caption_prompt is not None:
                inputs_map["prompt"] = caption_prompt

    if native_chat:
        classifier_inputs = prompt["4"]["inputs"]
        prompt["4"] = {
            "class_type": "LF_LocalChatCompletions",
            "inputs": {
                "prompt": classifier_inputs["prompt"],
                "url": effective_endpoint,
                "image": ["2", 0],
                "model": model,
                "temperature": classifier_inputs["temperature"],
                "max_tokens": classifier_inputs["max_tokens"],
            },
            "_meta": {"title": "Caption image with the local model"},
        }
        prompt["6"]["inputs"]["string"] = ["4", 0]
        if manage_model:
            prompt["load_lms"] = {
                "class_type": "LF_LMSLoadModel",
                "inputs": {"model": model, "url": effective_endpoint},
                "_meta": {"title": "Load the selected caption writer"},
            }
            prompt["4"]["inputs"]["model"] = ["load_lms", 0]
            prompt["release_lms"] = {
                "class_type": "LF_LMSUnloadModel",
                "inputs": {
                    "prompt": ["4", 0],
                    "instance_id": ["load_lms", 0],
                    "url": effective_endpoint,
                },
                "_meta": {"title": "Release the caption writer"},
            }
            prompt["6"]["inputs"]["string"] = ["release_lms", 0]
        else:
            prompt.pop("load_lms", None)
            prompt.pop("release_lms", None)


def _configure_download(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    """Produce a portable graph without staging an upload or contacting a model."""
    _configure(prompt, inputs, resolve_upload=False)
# endregion

# region Inputs
input_upload = WorkflowCell(
    node_id="2",
    id="source_path",
    value="Source image",
    shape="upload",
    props={
        "lfHtmlAttributes": {
            "accept": "image/*"
        },
        "lfLabel": "Source image",
    },
)
input_endpoint = WorkflowCell(
    node_id="4",
    id="endpoint",
    value="Chat completions endpoint",
    shape="textfield",
    required=False,
    props={
        "lfHtmlAttributes": {"name": "endpoint", "type": "text"},
        "lfLabel": "Chat completions endpoint",
        "lfValue": DEFAULT_ENDPOINT,
        "lfHelper": {
            "showWhenFocused": False,
            "value": "The address where the AI receives your image. Use an OpenAI-compatible chat-completions URL from your local server, a configured proxy, or LM Studio's native /api/v1/chat URL. The server needs a vision-capable model.",
        },
    },
)
input_max_tokens = WorkflowCell(
    node_id="4",
    id="max_tokens",
    value="Response token budget",
    shape="textfield",
    required=False,
    advanced=True,
    props={
        "lfHtmlAttributes": {
            "name": "max_tokens", "type": "number", "min": 20, "max": 8000, "step": 1,
        },
        "lfLabel": "Response token budget",
        "lfValue": str(DEFAULT_MAX_TOKENS),
        "lfHelper": {
            "showWhenFocused": False,
            "value": "Caps generated tokens, including reasoning and the final answer. The caption prompt controls caption length; this budget leaves room for the model to finish its answer.",
        },
    },
)
input_prompt = WorkflowCell(
    node_id="4",
    id="prompt",
    value="Caption instructions",
    shape="textfield",
    required=False,
    advanced=True,
    props={
        "lfLabel": "Caption instructions",
        "lfStyling": "textarea",
        "lfValue": DEFAULT_PROMPT,
        "lfHtmlAttributes": {"name": "prompt", "type": "text"},
    },
)
input_model = WorkflowCell(
    node_id="4",
    id="model",
    value="Model",
    shape="textfield",
    required=False,
    advanced=True,
    description="Optional LM Studio model key. Requires the native /api/v1/chat endpoint; blank uses the sole loaded LLM.",
    props={
        "lfLabel": "Model",
        "lfValue": "",
        "lfHtmlAttributes": {"name": "model", "type": "text"},
    },
)
input_manage_model = WorkflowCell(
    node_id="load_lms",
    id="manage_model",
    value="Load and release writer",
    shape="toggle",
    required=False,
    advanced=True,
    description=(
        "Load the selected downloaded LM Studio model, then release that exact "
        "instance after captioning. Also releases a matching instance already "
        "loaded. If captioning fails, it may remain loaded."
    ),
    props={"lfLabel": "Load and release writer", "lfValue": False},
)
# endregion

# region Outputs
output_string = WorkflowCell(
    id="string",
    node_id="6",
    shape="code",
    description="Caption",
    props={
        "lfLanguage": "markdown",
    }
)
# endregion

# region Workflow Definition
id = "caption_image_vision"
category = "LLM"
value = "Caption image (Vision)"
description = "Generates a caption for an input image using a vision-capable LLM model."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    card=WorkflowCardPresentation(
        summary="Caption one image with a vision-capable language model."
    ),
    inputs=[
        input_upload,
        input_endpoint,
        input_max_tokens,
        input_prompt,
        input_model,
        input_manage_model,
    ],
    outputs=[
        output_string,
    ],
    configure_prompt=_configure,
    configure_download=_configure_download,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
