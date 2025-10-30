"""Unit tests for workflow conversion logic.

These tests exercise the `_workflow_to_prompt` function to ensure the
conversion behavior is stable after the refactor.
"""

from ..services.workflow_conversion import _workflow_to_prompt


def test_workflow_conversion_nodes_list():
    workflow = {
        "nodes": [
            {
                "id": "n1",
                "class_type": "TypeA",
                "inputs": {"text": "hello"},
            }
        ]
    }

    prompt = _workflow_to_prompt(workflow)
    assert isinstance(prompt, dict)
    assert "n1" in prompt
    assert prompt["n1"]["class_type"] == "TypeA"
    assert prompt["n1"]["inputs"]["text"] == "hello"


def test_workflow_conversion_empty_or_malformed():
    # empty workflow should return empty prompt
    assert _workflow_to_prompt({}) == {}

    # malformed workflows (no nodes) also return empty prompt
    assert _workflow_to_prompt(None) == {}
