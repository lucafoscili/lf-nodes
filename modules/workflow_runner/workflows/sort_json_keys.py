from pathlib import Path
from typing import Any, Dict

from ..registry import InputValidationError, WorkflowCell, WorkflowNode
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
            parsed_json = convert_to_json(json_input)
            if parsed_json is None:
                raise InputValidationError(name)
            if isinstance(parsed_json, list):
                inputs_map["json_input"] = {"__value__": parsed_json}
            else:
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
        "lfFormatJSON": {
            "displayBorderOnError": True,
            "displayErrorAsTitle": True,
            "onBlur": True,
            "onInput": 800,
        },
        "lfHtmlAttributes": {
            "autocomplete": "off",
            "name": "json",
            "type": "text"
        },
        "lfLabel": "JSON Object",
        "lfHelper": {
            "showWhenFocused": False,
            "value": "The JSON object to sort.",
        },
        "lfStyle": ":host { height: 200px; }",
        "lfStyling": "textarea"
    },
)
input_ascending = WorkflowCell(
    node_id="1",
    id="ascending",
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
    node_id="2",
    id="sorted_json",
    shape="code",
    description="JSON Output",
    props={
        "lfLanguage": "json",
    }
)
# endregion

# region Workflow Definition
id = "sort_json_keys"
category = "JSON"
value = "Sort JSON keys"
description = "Sorts the keys of a JSON object."
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
    workflow_path=Path(__file__).resolve().parent / f"{id}.json",
    category=category
)
# endregion

WORKFLOW = node
