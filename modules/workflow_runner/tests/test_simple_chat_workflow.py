"""Runner chat boundary contracts; no browser, inference, or public-node changes."""

from copy import deepcopy
import json
import sys
import types

import pytest


# Match the declaration-only fixtures without loading Comfy's host/GPU stack.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows.simple_chat import WORKFLOW
from modules.workflow_runner.workflows.svg_generation_gemini import WORKFLOW as SVG_WORKFLOW


_HISTORY = [
    {"role": "user", "content": "Name one useful travel item."},
    {"role": "assistant", "content": "A notebook."},
]


@pytest.mark.parametrize("serialized", (False, True))
def test_runner_history_array_is_wrapped_for_the_public_node(serialized) -> None:
    graph = WORKFLOW.load_prompt()
    history = deepcopy(_HISTORY)

    WORKFLOW.configure_prompt(graph, {
        "chat": json.dumps(history) if serialized else history,
    })

    assert graph["11"]["class_type"] == "LF_LLMChat"
    assert graph["11"]["inputs"]["ui_widget"] == {"history": _HISTORY}
    assert graph["12"]["inputs"]["json_input"] == ["11", 0]
    graph["11"]["inputs"]["ui_widget"]["history"][0]["content"] = "Changed"
    assert history == _HISTORY


@pytest.mark.parametrize("serialized", (False, True))
def test_canonical_chat_object_preserves_config_and_message_metadata(serialized) -> None:
    graph = WORKFLOW.load_prompt()
    chat = {
        "config": {"temperature": 0.2},
        "history": [{"role": "user", "content": "Describe this.", "attachments": []}],
    }
    expected = deepcopy(chat)

    WORKFLOW.configure_prompt(graph, {"chat": json.dumps(chat) if serialized else chat})

    assert graph["11"]["inputs"]["ui_widget"] == expected
    graph["11"]["inputs"]["ui_widget"]["config"]["temperature"] = 0.9
    assert chat == expected


@pytest.mark.parametrize("chat", ([], "[]", {"history": []}, '{"config":{},"history":[]}'))
def test_empty_history_fails_clearly_before_mutating_the_graph(chat) -> None:
    graph = WORKFLOW.load_prompt()
    before = deepcopy(graph)

    with pytest.raises(InputValidationError, match="Send at least one chat message") as error:
        WORKFLOW.configure_prompt(graph, {"chat": chat})

    assert error.value.input_name == "chat"
    assert graph == before


@pytest.mark.parametrize(
    "chat",
    (
        None, True, 4, "", "not JSON", "null", "{}", {}, {"history": "text"},
        [None], ["message"], [{}], [{"content": "No role"}],
        [{"role": "", "content": "Empty role"}],
        [{"role": "user", "content": None}],
        [{"role": "user", "content": ["not widget text"]}],
    ),
)
def test_malformed_chat_is_a_field_validation_error(chat) -> None:
    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {"chat": chat})

    assert error.value.input_name == "chat"


def test_missing_chat_is_a_field_validation_error() -> None:
    with pytest.raises(InputValidationError) as error:
        WORKFLOW.configure_prompt(WORKFLOW.load_prompt(), {})

    assert error.value.input_name == "chat"


def test_downloaded_svg_graph_keeps_existing_outputs_with_the_saver_counter() -> None:
    graph = json.loads(SVG_WORKFLOW.workflow_path.read_text(encoding="utf-8"))

    assert graph["15"]["inputs"]["add_counter"] is True
    assert graph["15"]["inputs"]["add_timestamp"] is False
    assert graph["15"]["inputs"]["filename_prefix"] == ""
