"""CPU-only Caption Image wiring contracts; no LLM or image execution."""

from copy import deepcopy
import sys
import types

import pytest


# Declaration tests must not initialize Comfy's optional image/GPU helpers.
constants_module = types.ModuleType("modules.utils.constants")
constants_module.API_ROUTE_PREFIX = "/api/lf-nodes"
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.constants", constants_module)
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import caption_image_vision as workflow_module


@pytest.mark.parametrize(
    ("source", "canonical"),
    [
        ("source.png [input]", "source.png [input]"),
        (
            "LF_Nodes/Generate/source.png [output]",
            "LF_Nodes/Generate/source.png [output]",
        ),
        ("preview.png [temp]", "preview.png [temp]"),
        (
            "C:/external/source.png",
            "lf-workflow-runner/staged-images/sha256-example.png [input]",
        ),
    ],
)
def test_core_loader_uses_portable_reference_and_preserves_llm_defaults(
    monkeypatch: pytest.MonkeyPatch, source: str, canonical: str
) -> None:
    calls = []

    def resolve(inputs, name):
        calls.append((inputs[name], name))
        return canonical

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", resolve)
    graph = workflow_module.WORKFLOW.load_prompt()
    expected = deepcopy(graph)
    expected["2"]["inputs"]["image"] = canonical

    workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": source})

    assert calls == [(source, "source_path")]
    assert graph == expected
    assert graph["2"]["class_type"] == "LoadImage"
    assert graph["4"]["inputs"]["image"] == ["2", 0]
    assert graph["6"]["inputs"]["string"] == ["4", 2]


def test_invalid_source_fails_before_changing_the_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject(_inputs, name):
        raise InputValidationError(name)

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", reject)
    graph = workflow_module.WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(InputValidationError) as error:
        workflow_module.WORKFLOW.configure_prompt(graph, {})

    assert error.value.input_name == "source_path"
    assert graph == original


def test_shipped_caption_contract_keeps_its_same_origin_proxy_and_output() -> None:
    workflow = workflow_module.WORKFLOW
    graph = workflow.load_prompt()

    assert [(cell.id, cell.node_id) for cell in workflow.inputs] == [
        ("source_path", "2"), ("endpoint", "4"), ("max_tokens", "4"),
        ("prompt", "4"), ("model", "4"), ("manage_model", "load_lms"),
    ]
    endpoint = workflow.inputs[1]
    assert endpoint.required is False
    assert endpoint.props["lfValue"] == "/api/lf-nodes/proxy/kobold"
    assert endpoint.shape == "textfield"
    assert "OpenAI-compatible chat-completions" in endpoint.props["lfHelper"]["value"]
    assert [(cell.id, cell.node_id) for cell in workflow.outputs] == [("string", "6")]
    assert graph["4"]["inputs"]["url"] == "/api/lf-nodes/proxy/kobold"
    assert graph["4"]["inputs"]["max_tokens"] == 2048
    assert "model" not in graph["4"]["inputs"]
    assert graph["4"]["inputs"]["prompt"] == workflow_module.DEFAULT_PROMPT
    assert graph["4"]["class_type"] == "LF_ImageClassifier"
    for cell in workflow.inputs[3:]:
        assert cell.required is False
        assert cell.advanced is True
    assert workflow.inputs[4].props["lfValue"] == ""
    assert workflow.inputs[5].props["lfValue"] is False


def test_response_budget_is_an_optional_advanced_input() -> None:
    workflow = workflow_module.WORKFLOW
    budget = workflow.inputs[2]

    assert budget.id == "max_tokens"
    assert budget.required is False
    assert budget.advanced is True
    assert budget.props["lfValue"] == "2048"
    assert budget.props["lfHtmlAttributes"] == {
        "name": "max_tokens", "type": "number", "min": 20, "max": 8000, "step": 1,
    }
    helper = budget.props["lfHelper"]["value"]
    assert "including reasoning and the final answer" in helper
    assert "prompt controls caption length" in helper
    serialized = workflow.cells_as_dict("inputs")
    assert serialized["max_tokens"]["advanced"] is True
    assert serialized["max_tokens"]["required"] is False
    assert "advanced" not in serialized["source_path"]
    assert "advanced" not in serialized["endpoint"]


@pytest.mark.parametrize("max_tokens", (20, 2048, 8000, "20", "2048", " 8000 "))
def test_explicit_budget_changes_only_the_classifier_budget(monkeypatch, max_tokens) -> None:
    canonical = "source.png [input]"
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: canonical)
    graph = workflow_module.WORKFLOW.load_prompt()
    expected = deepcopy(graph)
    expected["2"]["inputs"]["image"] = canonical
    expected["4"]["inputs"]["max_tokens"] = int(max_tokens)

    workflow_module.WORKFLOW.configure_prompt(
        graph, {"source_path": canonical, "max_tokens": max_tokens},
    )

    assert graph == expected


def test_omitted_budget_preserves_a_configured_graph_value(monkeypatch) -> None:
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: "source.png [input]")
    graph = workflow_module.WORKFLOW.load_prompt()
    graph["4"]["inputs"]["max_tokens"] = 4096

    workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": "source.png [input]"})

    assert graph["4"]["inputs"]["max_tokens"] == 4096


@pytest.mark.parametrize("max_tokens", (
    None, False, True, 0, 19, 8001, -1, 20.5, 2048.0, [], {}, "", " ",
    "19", "8001", "20.5", "2e3", "many", float("inf"), float("nan"),
))
def test_invalid_budget_fails_before_resolving_source_or_changing_graph(monkeypatch, max_tokens) -> None:
    def unexpected_resolution(*_):
        pytest.fail("Response budget validation must run before image resolution.")

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", unexpected_resolution)
    graph = workflow_module.WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(InputValidationError) as error:
        workflow_module.WORKFLOW.configure_prompt(
            graph,
            {"source_path": "unused", "endpoint": "/configured/proxy", "max_tokens": max_tokens},
        )

    assert error.value.input_name == "max_tokens"
    assert graph == original


@pytest.mark.parametrize("endpoint", (
    "/api/lf-nodes/proxy/kobold",
    "http://127.0.0.1:5001/v1/chat/completions",
    "https://example.com/v1/chat/completions",
    "  /configured/proxy  ",
))
def test_explicit_endpoint_changes_only_the_classifier_url(monkeypatch, endpoint) -> None:
    canonical = "source.png [input]"
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: canonical)
    graph = workflow_module.WORKFLOW.load_prompt()
    expected = deepcopy(graph)
    expected["2"]["inputs"]["image"] = canonical
    expected["4"]["inputs"]["url"] = endpoint.strip()

    workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": canonical, "endpoint": endpoint})

    assert graph == expected


def test_omitted_endpoint_preserves_a_configured_graph_url(monkeypatch) -> None:
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: "source.png [input]")
    graph = workflow_module.WORKFLOW.load_prompt()
    graph["4"]["inputs"]["url"] = "/existing/custom/proxy"

    workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": "source.png [input]"})

    assert graph["4"]["inputs"]["url"] == "/existing/custom/proxy"


@pytest.mark.parametrize("endpoint", (None, False, 0, [], {}, "", "  ", "\r\n\t"))
def test_invalid_endpoint_fails_before_resolving_source_or_changing_graph(monkeypatch, endpoint) -> None:
    def unexpected_resolution(*_):
        pytest.fail("Endpoint validation must run before image resolution.")

    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", unexpected_resolution)
    graph = workflow_module.WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(InputValidationError) as error:
        workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": "unused", "endpoint": endpoint})

    assert error.value.input_name == "endpoint"
    assert graph == original


@pytest.mark.parametrize("endpoint", (
    "http://127.0.0.1:1234/api/v1/chat",
    "http://127.0.0.1:1234/api/v1/chat/",
    "https://example.test/lms/api/v1/chat?route=vision",
))
@pytest.mark.parametrize("model", ("", "writer-model"))
def test_native_chat_uses_existing_node_and_exact_description_handoff(monkeypatch, endpoint, model):
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: "pose.png [input]")
    graph = workflow_module.WORKFLOW.load_prompt()
    description_prompt = "Describe only body position, weight distribution and limb placement."

    workflow_module.WORKFLOW.configure_prompt(graph, {
        "source_path": "unused", "endpoint": endpoint, "model": model,
        "prompt": description_prompt, "max_tokens": "4096",
    })

    assert graph["4"] == {
        "class_type": "LF_LocalChatCompletions",
        "inputs": {
            "prompt": description_prompt,
            "url": endpoint,
            "model": model,
            "image": ["2", 0],
            "temperature": 0.7,
            "max_tokens": 4096,
        },
        "_meta": {"title": "Caption image with the local model"},
    }
    assert graph["6"]["inputs"]["string"] == ["4", 0]
    assert graph["2"]["inputs"]["image"] == "pose.png [input]"
    assert set(graph) == {"2", "4", "6"}


def test_native_chat_model_residency_matches_prompt_maker_policy(monkeypatch):
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: "pose.png [input]")
    graph = workflow_module.WORKFLOW.load_prompt()
    endpoint = "http://127.0.0.1:1234/api/v1/chat"
    inputs = {
        "source_path": "unused", "endpoint": endpoint,
        "model": "writer-model", "manage_model": True,
    }

    workflow_module.WORKFLOW.configure_prompt(graph, inputs)

    assert graph["load_lms"]["class_type"] == "LF_LMSLoadModel"
    assert graph["load_lms"]["inputs"] == {"model": "writer-model", "url": endpoint}
    assert graph["4"]["inputs"]["model"] == ["load_lms", 0]
    assert graph["release_lms"]["class_type"] == "LF_LMSUnloadModel"
    assert graph["release_lms"]["inputs"] == {
        "prompt": ["4", 0], "instance_id": ["load_lms", 0], "url": endpoint,
    }
    assert graph["6"]["inputs"]["string"] == ["release_lms", 0]


    # Turning residency management off removes lifecycle dependencies.
    workflow_module.WORKFLOW.configure_prompt(graph, {**inputs, "manage_model": False})
    assert graph["4"]["inputs"]["model"] == "writer-model"
    assert graph["6"]["inputs"]["string"] == ["4", 0]
    assert "load_lms" not in graph
    assert "release_lms" not in graph


def test_portable_defaults_do_not_require_an_upload_for_catalogue_readiness():
    graph = workflow_module.WORKFLOW.load_prompt()
    workflow_module.WORKFLOW.configure_download(graph, {})
    assert graph["2"]["inputs"]["image"] == "source_path.png"
    assert graph["4"]["class_type"] == "LF_ImageClassifier"


def test_custom_instructions_keep_classifier_output_contract(monkeypatch):
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: "source.png [input]")
    graph = workflow_module.WORKFLOW.load_prompt()

    workflow_module.WORKFLOW.configure_prompt(graph, {
        "source_path": "unused", "prompt": "Describe the visible pose.",
    })

    assert graph["4"]["class_type"] == "LF_ImageClassifier"
    assert graph["4"]["inputs"]["prompt"] == "Describe the visible pose."
    assert graph["6"]["inputs"]["string"] == ["4", 2]


@pytest.mark.parametrize(("overrides", "input_name"), [
    ({"prompt": ""}, "prompt"),
    ({"prompt": None}, "prompt"),
    ({"prompt": []}, "prompt"),
    ({"model": None}, "model"),
    ({"model": []}, "model"),
    ({"manage_model": "true"}, "manage_model"),
    ({"manage_model": 1}, "manage_model"),
])
def test_invalid_optional_controls_fail_before_upload_resolution(monkeypatch, overrides, input_name):
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: pytest.fail("Must validate before upload staging."))
    graph = workflow_module.WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(InputValidationError) as error:
        workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": "unused", **overrides})

    assert error.value.input_name == input_name
    assert graph == original


@pytest.mark.parametrize("overrides", (
    {"model": "writer-model"},
    {"manage_model": True},
    {"endpoint": "http://127.0.0.1:1234/api/v1/chat", "manage_model": True},
))
def test_model_selection_failures_precede_staging(monkeypatch, overrides):
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: pytest.fail("Must validate before upload staging."))
    graph = workflow_module.WORKFLOW.load_prompt()
    original = deepcopy(graph)

    with pytest.raises(ValueError, match="LM Studio"):
        workflow_module.WORKFLOW.configure_prompt(graph, {"source_path": "unused", **overrides})

    assert graph == original


def test_download_keeps_native_binding_without_staging_upload(monkeypatch):
    monkeypatch.setattr(workflow_module, "resolve_load_image_reference", lambda *_: pytest.fail("Download must not stage uploads."))
    graph = workflow_module.WORKFLOW.load_prompt()

    workflow_module.WORKFLOW.configure_download(graph, {
        "source_path": "C:/external/pose.png", "prompt": "Describe the visible pose.",
        "endpoint": "http://127.0.0.1:1234/api/v1/chat", "model": "writer-model",
        "manage_model": True,
    })

    assert graph["2"]["inputs"]["image"] == "source_path.png"
    assert graph["4"]["class_type"] == "LF_LocalChatCompletions"
    assert graph["4"]["inputs"]["prompt"] == "Describe the visible pose."
    assert graph["4"]["inputs"]["model"] == ["load_lms", 0]
    assert graph["6"]["inputs"]["string"] == ["release_lms", 0]
