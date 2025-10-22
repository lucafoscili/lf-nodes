from typing import Any, Dict

from ..registry import InputValidationError, WorkflowCell, resolve_user_path, WorkflowNode
from ...utils.helpers.conversion import convert_to_json

# region Workflow Config
def _configure(prompt: Dict[str, Any], inputs: Dict[str, Any]) -> None:
    for (node_id, node) in prompt.items():
        if not isinstance(node, dict):
            continue

        inputs_map = node.setdefault("inputs", {})

        if node_id == "1":  # JSON object
            name = "json"
            json_input = inputs.get(name)
            if not json_input:
                raise InputValidationError(name)
            if not isinstance(json_input, str):
                raise InputValidationError(name)
            if isinstance(json_input, str):
                parsed_json = convert_to_json(json_input)
            elif isinstance(json_input, dict):
                parsed_json = json_input
            else:
                raise InputValidationError(name)
            inputs_map["json_input"] = parsed_json

        if node_id == "1":  # Sort ascending
            name = "ascending"
            ascending = inputs.get(name)
            inputs_map["ascending"] = bool(ascending)
# endregion

# region Inputs
input_json = WorkflowCell(
    node_id="1",
    id="json",
    value="JSON Object",
    shape="textfield",
    props={
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "type": "text"
        },
        "lfLabel": "JSON Object",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "The JSON object to sort.",
        },
        "lfStyling": "textarea"
    },
)
input_ascending = WorkflowCell(
    id="ascending",
    node_id="1",
    shape="toggle",
    value="Sort ascending",
    description="Sets whether to sort the JSON keys in ascending order.",
    props={
        "lfLabel": "Sort ascending",
        "lfValue": True,
    },
)
# endregion

# region Outputs
output_json = WorkflowCell(
    id="sorted_json",
    node_id="2",
    shape="code",
    description="JSON Output",
    props={
        "lfLanguage": "json",
    }
)
# endregion

# region Workflow Definition
id = "sort-json-keys"
category = "JSON"
value = "Sort JSON keys"
description = "Sorts the keys of a JSON object."
path = resolve_user_path("default", "workflows", f"{value}.json")
node = WorkflowNode(
    id=id,
    value=value,
    description=description,
    inputs=[
        input_json,
        input_ascending,
    ],
    outputs=[
        output_json,
    ],
    configure_prompt=_configure,
    workflow_path=path,
    category=category
)
# endregion

WORKFLOW = node
