from pathlib import Path
from typing import Any, Dict

from ..services.registry import InputValidationError, WorkflowCell, WorkflowNode
from .utils import resolve_load_image_reference

DEFAULT_ENDPOINT = "/api/lf-nodes/proxy/kobold"
DEFAULT_MAX_TOKENS = 2048

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    endpoint = None
    if "endpoint" in inputs:
        endpoint = inputs["endpoint"]
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise InputValidationError("endpoint")
        endpoint = endpoint.strip()

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

    source_image = resolve_load_image_reference(inputs, "source_path")
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
            "value": "The address where the AI receives your image. Use an OpenAI-compatible chat-completions URL from your local server, or a proxy you have configured. The server needs a vision-capable model.",
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
    inputs=[
        input_upload,
        input_endpoint,
        input_max_tokens,
    ],
    outputs=[
        output_string,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
