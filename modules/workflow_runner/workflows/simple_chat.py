from pathlib import Path
from typing import Any, Dict

from ..registry import InputValidationError, WorkflowCell, WorkflowNode

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "11":  # JSON object
            name = "chat"
            stringified_json_input = inputs.get(name)
            
            if not stringified_json_input:
                raise InputValidationError(name)
            
            inputs_map["ui_widget"] = stringified_json_input
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
