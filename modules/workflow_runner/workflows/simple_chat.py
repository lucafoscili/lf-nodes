import json

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

from ..services.registry import (
    InputValidationError,
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowNode,
)

# region Workflow Config
class _ChatInputError(InputValidationError):
    def __init__(self, message: str) -> None:
        super().__init__("chat")
        self.args = (message,)


def _normalize_chat(value: Any) -> Dict[str, Any]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise _ChatInputError("Chat history must be valid JSON.") from error
    if isinstance(value, list):
        value = {"history": value}
    if not isinstance(value, dict) or not isinstance(value.get("history"), list):
        raise _ChatInputError(
            "Chat history must be an array or an object containing a history array."
        )
    if not value["history"]:
        raise _ChatInputError("Send at least one chat message before running this workflow.")
    for message in value["history"]:
        if (
            not isinstance(message, dict)
            or not isinstance(message.get("role"), str)
            or not message["role"].strip()
            or not isinstance(message.get("content"), str)
        ):
            raise _ChatInputError("Each chat message must have a role and text content.")
    return deepcopy(value)


def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    chat = _normalize_chat(inputs.get("chat"))
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "11":  # The public node consumes the canonical widget object.
            inputs_map["ui_widget"] = chat
# endregion

# region Inputs
input_chat = WorkflowCell(
    node_id="11",
    id="chat",
    value="Chat widget",
    shape="chat",
)
# endregion

# region Outputs
output_json = WorkflowCell(
    node_id="12",
    id="json",
    shape="code",
    description="Chat history",
    props={
        "lfLanguage": "json",
    }
)
# endregion

# region Workflow Definition
id = "simple_chat"
category = "LLM"
value = "Simple chat"
description = "A simple chat workflow that outputs chat history."
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    card=WorkflowCardPresentation(
        summary="Collect a chat conversation and return its history as JSON."
    ),
    inputs=[
        input_chat,
    ],
    outputs=[
        output_json,
    ],
    configure_prompt=_configure,
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
