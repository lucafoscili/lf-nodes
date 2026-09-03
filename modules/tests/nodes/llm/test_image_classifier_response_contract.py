"""Classifier response failures must not become successful empty captions."""
import importlib
import json

import pytest
import torch

from modules.utils.constants import Input, INT_MAX
from modules.utils.helpers.api.handle_response import handle_response, require_response_text


classifier = importlib.import_module("modules.nodes.llm.image_classifier")
url_helpers = importlib.import_module("modules.utils.helpers.api.resolve_url")


def test_published_classifier_schema_and_socket_contract_remain_unchanged():
    node = classifier.LF_ImageClassifier
    schema = node.INPUT_TYPES()
    normalized = {
        group: {
            name: (config[0], {key: value for key, value in config[1].items() if key != "tooltip"})
            for name, config in inputs.items()
        }
        for group, inputs in schema.items() if group != "hidden"
    }
    assert normalized == {
        "required": {
            "image": (Input.IMAGE, {"default": None}),
            "temperature": (Input.FLOAT, {"max": 1.901, "min": 0.1, "step": 0.1, "round": 0.1, "default": 0.7}),
            "max_tokens": (Input.INTEGER, {"max": 8000, "min": 20, "step": 10, "default": 500}),
            "prompt": (Input.STRING, {"multiline": True, "default": ""}),
            "seed": (Input.INTEGER, {"default": 42, "min": 0, "max": INT_MAX}),
            "url": (Input.STRING, {"default": "http://localhost:5001/v1/chat/completions"}),
        },
        "optional": {
            "character_bio": (Input.STRING, {"multiline": True, "default": ""}),
            "ui_widget": (Input.LF_CODE, {"default": ""}),
        },
    }
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert node.RETURN_TYPES == (Input.JSON, Input.JSON, Input.STRING)
    assert node.RETURN_NAMES == ("request_json", "response_json", "message")
    assert not hasattr(node, "INPUT_IS_LIST")
    assert not hasattr(node, "OUTPUT_IS_LIST")
    assert len(node.OUTPUT_TOOLTIPS) == 3


class Response:
    def __init__(self, data, status=200):
        self.data = data
        self.status_code = status

    def json(self):
        if isinstance(self.data, Exception):
            raise self.data
        return self.data


@pytest.fixture
def invoke(monkeypatch):
    events = []
    calls = []
    monkeypatch.setattr(classifier, "safe_send_sync", lambda *args: events.append(args))
    monkeypatch.setattr(classifier, "build_openai_multimodal_content", lambda *_: [{"type": "text", "text": "Describe this image."}])

    def run(data, status=200, url="http://localhost.test/v1/chat/completions"):
        def post(*args, **kwargs):
            calls.append((args, kwargs))
            return Response(data, status)

        monkeypatch.setattr(classifier.requests, "post", post)
        return classifier.LF_ImageClassifier().on_exec(
            image=torch.zeros((1, 2, 2, 3)), temperature=0.7,
            max_tokens=2048, prompt="Describe this image.", seed=42,
            url=url,
        )

    return run, events, calls


@pytest.mark.parametrize("content", ("", " \n\t", None))
def test_empty_length_limited_answer_fails_clearly_without_retry_or_success_event(invoke, content):
    run, events, calls = invoke
    data = {"choices": [{"finish_reason": "length", "message": {"content": content, "reasoning_content": "Private reasoning is not the caption."}}]}
    with pytest.raises(ValueError, match="exhausted its response token budget.*Increase max_tokens"):
        run(data)
    assert len(calls) == 1
    assert events == []


@pytest.mark.parametrize("data", (
    {"choices": [{"finish_reason": "stop", "message": {"content": ""}}]},
    {"choices": [{"finish_reason": "stop", "message": {"content": None}}]},
    {"choices": [{"finish_reason": "stop", "message": {"reasoning_content": "No answer yet."}}]},
    {"choices": [{"finish_reason": "tool_calls", "message": {"tool_calls": [{"function": {"name": "describe"}}]}}]},
    {"choices": []},
    {"choices": [{}]},
    {"choices": [{"message": None}]},
    {"choices": None},
    {"text": "   "},
))
def test_no_answer_is_not_a_caption_or_raw_envelope(invoke, data):
    run, events, _ = invoke
    with pytest.raises(ValueError, match="no answer text"):
        run(data)
    assert events == []


@pytest.mark.parametrize("reason", ("stop", "length"))
def test_real_answer_and_raw_response_are_preserved_verbatim(invoke, reason):
    run, events, calls = invoke
    answer = "  An orange flame above dark crossed logs.\n"
    data = {"choices": [{"finish_reason": reason, "message": {"content": answer, "reasoning_content": "Internal analysis."}}]}
    request, response, message = run(data)
    assert message == answer
    assert response is data
    assert request["max_tokens"] == 2048
    assert len(calls) == 1
    assert events == [("imageclassifier", {"value": answer}, None)]


@pytest.mark.parametrize("data", (
    {"results": [{"text": "Campfire icon."}]},
    {"choices": [{"text": "Campfire icon."}]},
))
def test_legacy_text_response_still_works(invoke, data):
    run, _, _ = invoke
    assert run(data)[2] == "Campfire icon."


@pytest.mark.parametrize("status", (400, 401, 403, 429, 500))
def test_http_errors_fail_instead_of_becoming_caption_text(invoke, status):
    run, events, calls = invoke
    with pytest.raises(ValueError, match=f"HTTP status {status}"):
        run({"error": "provider detail"}, status)
    assert len(calls) == 1
    assert events == []


def test_non_json_http_error_still_reports_the_http_failure(invoke):
    run, events, calls = invoke
    with pytest.raises(ValueError, match="HTTP status 502"):
        run(ValueError("Not JSON"), 502)
    assert len(calls) == 1
    assert events == []


def test_general_response_parser_retains_legacy_empty_behavior():
    data = {"choices": [{"finish_reason": "length", "message": {"content": ""}}]}
    assert handle_response(Response(data), method="POST") == (200, "POST", "")
    with pytest.raises(ValueError, match="response token budget"):
        require_response_text(data, "")


@pytest.mark.parametrize("url", (
    "/api/lf-nodes/proxy/kobold",
    "/lf-nodes/proxy/kobold/v1/chat/completions",
))
def test_caption_authenticates_only_internal_proxy_transport(invoke, monkeypatch, url):
    monkeypatch.setattr(url_helpers, "read_secret", lambda name: "test-only-secret" if name == "LF_PROXY_SECRET" else None)
    run, _, calls = invoke
    data = {"choices": [{"message": {"content": "Campfire icon."}}]}
    result = run(data, url=url)
    options = calls[0][1]
    assert options["headers"]["X-LF-Proxy-Secret"] == "test-only-secret"
    assert options["allow_redirects"] is False
    assert "test-only-secret" not in json.dumps(result)
    assert "X-LF-Proxy-Secret" not in classifier.HEADERS


@pytest.mark.parametrize("url", (
    "http://localhost.test/v1/chat/completions",
    "https://example.test/api/lf-nodes/proxy/kobold",
    "http://127.0.0.1:8188/api/lf-nodes/proxy/kobold",
    "//example.test/api/lf-nodes/proxy/kobold",
    "/api/lf-nodes/proxy-other/kobold",
    "/other/endpoint",
    "/api/lf-nodes/proxy/../../../../other",
    "/lf-nodes/proxy/kobold/../other",
    "/api/lf-nodes/proxy/kobold/./v1/chat/completions",
    "/api/lf-nodes/proxy/%2e%2e/%2e%2e/other",
    "/api/lf-nodes/proxy/kobold/%252e%252e/other",
    "/api/lf-nodes/proxy/kobold/%2f..%2fother",
    "/api/lf-nodes/proxy/kobold/..\\other",
    "/api/lf-nodes/proxy/kobold\t/../../../other",
))
def test_non_internal_urls_never_read_or_receive_the_proxy_secret(monkeypatch, url):
    def forbidden_read(_name):
        pytest.fail("Do not look up proxy credentials for arbitrary endpoint URLs.")

    monkeypatch.setattr(url_helpers, "read_secret", forbidden_read)
    headers = {"Content-Type": "application/json"}
    options = url_helpers.local_proxy_request_options(url, headers)
    assert options == {"headers": headers}
    assert options["headers"] is not headers


@pytest.mark.parametrize("fallback", (None, "legacy-secret"))
def test_internal_proxy_preserves_secret_disabled_or_legacy_secret_configuration(monkeypatch, fallback):
    monkeypatch.setattr(url_helpers, "read_secret", lambda name: fallback if name == "GEMINI_PROXY_SECRET" else None)
    options = url_helpers.local_proxy_request_options("/api/lf-nodes/proxy/kobold", {})
    if fallback:
        assert options == {"headers": {"X-LF-Proxy-Secret": fallback}, "allow_redirects": False}
    else:
        assert options == {"headers": {}}
