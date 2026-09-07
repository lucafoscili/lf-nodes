from __future__ import annotations

import importlib
import json

import pytest
import requests
import torch

from modules.utils.constants import Input


chat_module = importlib.import_module(
    "modules.nodes.llm.local_chat_completions"
)
api_module = importlib.import_module("modules.utils.helpers.api")
transport_module = importlib.import_module(
    "modules.utils.helpers.api.local_chat_completion"
)
multimodal_module = importlib.import_module(
    "modules.utils.helpers.api.build_multimodal_content"
)


class Response:
    def __init__(self, data, status_code: int = 200):
        self.data = data
        self.status_code = status_code

    def json(self):
        if isinstance(self.data, Exception):
            raise self.data
        return self.data


def _success(text: str = "A generated prompt.") -> dict:
    return {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"content": text},
            }
        ]
    }


def _native_success(text: str = "A generated prompt.") -> dict:
    return {
        "model_instance_id": "local-model",
        "output": [
            {"type": "message", "content": "Discarded draft."},
            {"type": "reasoning", "content": "Private reasoning."},
            {"type": "tool_call", "content": "Private tool call."},
            {"type": "message", "content": text},
        ],
        "stats": {
            "total_output_tokens": 12,
            "reasoning_output_tokens": 3,
        },
    }


def _native_models(*loaded_llm_ids: str) -> dict:
    return {
        "models": [
            {
                "type": "embedding",
                "key": "local-embedding",
                "loaded_instances": [
                    {"id": "local-embedding", "config": {}}
                ],
            },
            {
                "type": "llm",
                "key": "downloaded-but-unloaded",
                "loaded_instances": [],
            },
            {
                "type": "llm",
                "key": "loaded-model",
                "loaded_instances": [
                    {"id": instance_id, "config": {}}
                    for instance_id in loaded_llm_ids
                ],
            },
        ]
    }


def _strip_tooltips(schema: dict) -> dict:
    return {
        group: {
            name: (
                config[0],
                {
                    key: value
                    for key, value in config[1].items()
                    if key != "tooltip"
                },
            )
            for name, config in inputs.items()
        }
        for group, inputs in schema.items()
        if group != "hidden"
    }


def _capture_transport(
    monkeypatch: pytest.MonkeyPatch,
    data=None,
    *,
    status_code: int = 200,
) -> tuple[list[dict], list[tuple]]:
    calls: list[dict] = []
    events: list[tuple] = []

    def post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        return Response(_success() if data is None else data, status_code)

    monkeypatch.setattr(transport_module.requests, "post", post)
    monkeypatch.setattr(
        chat_module,
        "safe_send_sync",
        lambda *args: events.append(args),
    )
    return calls, events


def test_published_schema_mapping_and_output_contract() -> None:
    node = chat_module.LF_LocalChatCompletions
    schema = node.INPUT_TYPES()

    assert _strip_tooltips(schema) == {
        "required": {
            "prompt": (Input.STRING, {"default": "", "multiline": True}),
            "url": (
                Input.STRING,
                {
                    "default": (
                        "http://127.0.0.1:1234/v1/chat/completions"
                    )
                },
            ),
        },
        "optional": {
            "system_message": (
                Input.STRING,
                {"default": "", "multiline": True},
            ),
            "image": (Input.IMAGE, {}),
            "model": (Input.STRING, {"default": ""}),
            "temperature": (
                Input.FLOAT,
                {
                    "default": 0.2,
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1,
                },
            ),
            "max_tokens": (Input.INTEGER, {"default": 4096, "min": 1}),
            "reasoning": (
                ["auto", "off", "on"],
                {"default": "auto"},
            ),
            "timeout": (Input.INTEGER, {"default": 120, "min": 1}),
            "ui_widget": (Input.LF_CODE, {"default": ""}),
        },
    }
    assert list(schema["optional"]) == [
        "system_message",
        "image",
        "model",
        "temperature",
        "max_tokens",
        "timeout",
        "ui_widget",
        "reasoning",
    ]
    assert schema["hidden"] == {"node_id": "UNIQUE_ID"}
    assert node.CATEGORY == "✨ LF Nodes/LLM"
    assert node.FUNCTION == "on_exec"
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_TYPES == (Input.STRING, Input.JSON)
    assert node.RETURN_NAMES == ("text", "response_json")
    assert node.OUTPUT_IS_LIST == (False, False)
    assert len(node.OUTPUT_TOOLTIPS) == 2
    assert not hasattr(node, "OUTPUT_NODE")
    assert chat_module.NODE_CLASS_MAPPINGS == {
        "LF_LocalChatCompletions": node,
    }
    assert chat_module.NODE_DISPLAY_NAME_MAPPINGS == {
        "LF_LocalChatCompletions": "Local chat completions",
    }


def test_headless_transport_helper_is_exported_without_publishing_node_ui(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response_data = _success("Headless answer.")
    calls: list[dict] = []

    def post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        return Response(response_data)

    monkeypatch.setattr(transport_module.requests, "post", post)
    monkeypatch.setattr(
        chat_module,
        "safe_send_sync",
        lambda *_args: pytest.fail(
            "The transport helper must not publish Comfy UI state."
        ),
    )

    assert (
        api_module.request_local_chat_completion
        is transport_module.request_local_chat_completion
    )
    result = transport_module.request_local_chat_completion(
        "Prompt",
        "http://localhost.test/v1/chat/completions",
    )

    assert result == ("Headless answer.", response_data)
    assert len(calls) == 1


def test_text_only_request_normalizes_list_wrapped_scalars_and_persists_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    answer = "  exact generated prompt\n"
    response_data = _success(answer)
    calls, events = _capture_transport(monkeypatch, response_data)

    result = chat_module.LF_LocalChatCompletions().on_exec(
        prompt=["  Keep this input exact.  "],
        url=["  http://localhost.test/v1/chat/completions  "],
        system_message=[""],
        model=[""],
        temperature=[0.0],
        max_tokens=[8192],
        timeout=[45],
        node_id=[["node-7"]],
    )

    assert calls == [
        {
            "url": "http://localhost.test/v1/chat/completions",
            "json": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "  Keep this input exact.  ",
                            }
                        ],
                    }
                ],
                "temperature": 0.0,
                "max_tokens": 8192,
            },
            "timeout": 45,
            "headers": {"Content-Type": "application/json"},
        }
    ]
    payload = {"value": answer}
    assert events == [
        ("localchatcompletions", payload, [["node-7"]]),
    ]
    assert result == {
        "ui": {"lf_output": [payload]},
        "result": (answer, response_data),
    }


def test_one_reference_image_is_sent_before_the_exact_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = torch.zeros((1, 2, 3, 3), dtype=torch.float32)
    encoded: list[torch.Tensor] = []

    def encode(images: list[torch.Tensor]) -> list[str]:
        encoded.extend(images)
        return ["only-frame"]

    monkeypatch.setattr(multimodal_module, "tensor_to_base64", encode)
    calls, _ = _capture_transport(monkeypatch)

    chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Describe the reference.",
        url="http://localhost.test/v1/chat/completions",
        image=image,
    )

    assert encoded == [image]
    assert calls[0]["json"]["messages"][-1]["content"] == [
        {
            "type": "image_url",
            "image_url": {
                "url": "data:image/png;base64,only-frame"
            },
        },
        {"type": "text", "text": "Describe the reference."},
    ]


def test_every_nested_heterogeneous_reference_is_sent_in_source_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_batch = torch.stack(
        (
            torch.zeros((2, 3, 3), dtype=torch.float32),
            torch.ones((2, 3, 3), dtype=torch.float32),
        )
    )
    third = torch.full((1, 4, 5, 4), 0.5, dtype=torch.float32)
    encoded: list[torch.Tensor] = []

    def encode(images: list[torch.Tensor]) -> list[str]:
        encoded.extend(images)
        return [f"frame-{index}" for index in range(len(images))]

    monkeypatch.setattr(multimodal_module, "tensor_to_base64", encode)
    calls, _ = _capture_transport(monkeypatch)

    result = chat_module.LF_LocalChatCompletions().on_exec(
        prompt=["Use all references."],
        url=["http://localhost.test/v1/chat/completions"],
        image=[[first_batch], [third]],
    )

    assert len(encoded) == 3
    assert [tuple(item.shape) for item in encoded] == [
        (1, 2, 3, 3),
        (1, 2, 3, 3),
        (1, 4, 5, 4),
    ]
    assert torch.count_nonzero(encoded[0]) == 0
    assert torch.count_nonzero(encoded[1]) == encoded[1].numel()
    assert calls[0]["json"]["messages"][-1]["content"] == [
        {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,frame-0"},
        },
        {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,frame-1"},
        },
        {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,frame-2"},
        },
        {"type": "text", "text": "Use all references."},
    ]
    assert "data:image" not in json.dumps(result)


def test_nonempty_system_message_and_model_are_included_verbatim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, _ = _capture_transport(monkeypatch)

    chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Write it.",
        url="http://localhost.test/v1/chat/completions",
        system_message="  Follow the supplied format exactly.  ",
        model="  local-vision-model  ",
    )

    payload = calls[0]["json"]
    assert payload["model"] == "local-vision-model"
    assert payload["messages"] == [
        {
            "role": "system",
            "content": "  Follow the supplied format exactly.  ",
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": "Write it."}],
        },
    ]


def test_lm_studio_native_request_uses_supported_vision_and_reasoning_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image = torch.stack(
        (
            torch.zeros((2, 3, 3), dtype=torch.float32),
            torch.ones((2, 3, 3), dtype=torch.float32),
        )
    )
    monkeypatch.setattr(
        multimodal_module,
        "tensor_to_base64",
        lambda _images: ["native-frame-1", "native-frame-2"],
    )
    answer = "  exact native answer\n"
    response_data = _native_success(answer)
    calls, events = _capture_transport(monkeypatch, response_data)
    monkeypatch.setattr(
        transport_module.requests,
        "get",
        lambda *_args, **_kwargs: pytest.fail(
            "An explicit native model must skip model discovery."
        ),
    )

    result = chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Describe the reference.",
        url="http://localhost.test/proxy/api/v1/chat/",
        system_message="Use the schema.",
        image=image,
        model="vision-model",
        temperature=0.3,
        max_tokens=5000,
        reasoning="off",
        timeout=180,
        node_id="native-node",
    )

    assert calls == [
        {
            "url": "http://localhost.test/proxy/api/v1/chat/",
            "json": {
                "model": "vision-model",
                "input": [
                    {
                        "type": "text",
                        "content": "Describe the reference.",
                    },
                    {
                        "type": "image",
                        "data_url": (
                            "data:image/png;base64,native-frame-1"
                        ),
                    },
                    {
                        "type": "image",
                        "data_url": (
                            "data:image/png;base64,native-frame-2"
                        ),
                    },
                ],
                "temperature": 0.3,
                "max_output_tokens": 5000,
                "store": False,
                "system_prompt": "Use the schema.",
                "reasoning": "off",
            },
            "timeout": 180,
            "headers": {"Content-Type": "application/json"},
        }
    ]
    payload = {"value": answer}
    assert events == [("localchatcompletions", payload, "native-node")]
    assert result == {
        "ui": {"lf_output": [payload]},
        "result": (answer, response_data),
    }
    assert "native-frame" not in json.dumps(result)
    assert "Discarded draft" not in result["result"][0]
    assert "Private reasoning" not in result["result"][0]


def test_blank_native_model_resolves_the_sole_loaded_llm_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    operations: list[dict] = []
    events: list[tuple] = []

    def get(url, **kwargs):
        operations.append({"method": "GET", "url": url, **kwargs})
        return Response(_native_models("qwen-loaded-instance"))

    def post(url, **kwargs):
        operations.append({"method": "POST", "url": url, **kwargs})
        return Response(_native_success())

    monkeypatch.setattr(transport_module.requests, "get", get)
    monkeypatch.setattr(transport_module.requests, "post", post)
    monkeypatch.setattr(
        chat_module,
        "safe_send_sync",
        lambda *args: events.append(args),
    )

    result = chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Prompt",
        url="http://localhost.test/proxy/api/v1/chat/?token=test",
        model="  ",
        timeout=45,
        node_id="auto-model-node",
    )

    assert operations == [
        {
            "method": "GET",
            "url": (
                "http://localhost.test/proxy/api/v1/models?token=test"
            ),
            "timeout": 45,
            "headers": {"Content-Type": "application/json"},
        },
        {
            "method": "POST",
            "url": (
                "http://localhost.test/proxy/api/v1/chat/?token=test"
            ),
            "json": {
                "model": "qwen-loaded-instance",
                "input": [{"type": "text", "content": "Prompt"}],
                "temperature": 0.2,
                "max_output_tokens": 4096,
                "store": False,
            },
            "timeout": 45,
            "headers": {"Content-Type": "application/json"},
        },
    ]
    payload = {"value": "A generated prompt."}
    assert events == [
        ("localchatcompletions", payload, "auto-model-node")
    ]
    assert result == {
        "ui": {"lf_output": [payload]},
        "result": ("A generated prompt.", _native_success()),
    }


@pytest.mark.parametrize(
    ("models", "message"),
    (
        (_native_models(), "reports no loaded LLM instances"),
        (
            _native_models("first-instance", "second-instance"),
            r"reports multiple loaded LLM instances \(2\)",
        ),
    ),
)
def test_blank_native_model_requires_exactly_one_loaded_llm(
    monkeypatch: pytest.MonkeyPatch,
    models: dict,
    message: str,
) -> None:
    posts: list[dict] = []
    monkeypatch.setattr(
        transport_module.requests,
        "get",
        lambda *_args, **_kwargs: Response(models),
    )
    monkeypatch.setattr(
        transport_module.requests,
        "post",
        lambda *args, **kwargs: posts.append({"args": args, **kwargs}),
    )

    with pytest.raises(ValueError, match=message):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/api/v1/chat",
            model="",
        )

    assert posts == []


@pytest.mark.parametrize(
    ("data", "message"),
    (
        (ValueError("not json"), "not valid JSON"),
        ({"data": []}, "malformed JSON"),
        (
            {
                "models": [
                    {"type": "llm", "loaded_instances": [{"id": ""}]}
                ]
            },
            "malformed JSON",
        ),
    ),
)
def test_blank_native_model_rejects_malformed_model_lookup(
    monkeypatch: pytest.MonkeyPatch,
    data: object,
    message: str,
) -> None:
    monkeypatch.setattr(
        transport_module.requests,
        "get",
        lambda *_args, **_kwargs: Response(data),
    )
    monkeypatch.setattr(
        transport_module.requests,
        "post",
        lambda *_args, **_kwargs: pytest.fail(
            "Malformed model discovery must prevent chat inference."
        ),
    )

    with pytest.raises(ValueError, match=message):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/api/v1/chat",
            model="",
        )


def test_blank_native_model_surfaces_model_lookup_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        transport_module.requests,
        "get",
        lambda *_args, **_kwargs: Response(
            {"error": {"message": "Model service unavailable."}},
            status_code=503,
        ),
    )
    monkeypatch.setattr(
        transport_module.requests,
        "post",
        lambda *_args, **_kwargs: pytest.fail(
            "Failed model discovery must prevent chat inference."
        ),
    )

    with pytest.raises(ValueError) as raised:
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/api/v1/chat",
            model="",
        )

    assert str(raised.value) == (
        "LM Studio model lookup failed with HTTP status 503. "
        "Provider said: Model service unavailable."
    )


def test_blank_native_model_surfaces_model_lookup_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        transport_module.requests,
        "get",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            requests.ConnectionError("offline")
        ),
    )
    monkeypatch.setattr(
        transport_module.requests,
        "post",
        lambda *_args, **_kwargs: pytest.fail(
            "Failed model discovery must prevent chat inference."
        ),
    )

    with pytest.raises(ValueError, match="model lookup failed"):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/api/v1/chat",
            model="",
        )


def test_lm_studio_native_auto_omits_reasoning_override_and_empty_system(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, _ = _capture_transport(monkeypatch, _native_success())

    chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Prompt",
        url="http://localhost.test/api/v1/chat",
        model="local-model",
        reasoning="auto",
    )

    assert "reasoning" not in calls[0]["json"]
    assert "system_prompt" not in calls[0]["json"]
    assert calls[0]["json"]["input"] == [
        {"type": "text", "content": "Prompt"}
    ]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    (
        (
            {
                "url": "http://localhost.test/api/v1/chat",
                "model": "local-model",
                "temperature": 1.1,
            },
            "temperature must be between 0 and 1",
        ),
        (
            {
                "url": "http://localhost.test/v1/chat/completions",
                "reasoning": "off",
            },
            "reasoning off/on requires an LM Studio native",
        ),
        (
            {
                "url": "http://localhost.test/api/v1/chat",
                "model": "local-model",
                "reasoning": "sometimes",
            },
            "reasoning must be one of",
        ),
    ),
)
def test_native_only_controls_fail_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    kwargs: dict,
    message: str,
) -> None:
    def unexpected_post(*_args, **_kwargs):
        pytest.fail("Invalid native chat input must fail before transport.")

    monkeypatch.setattr(transport_module.requests, "post", unexpected_post)

    with pytest.raises((TypeError, ValueError), match=message):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            **kwargs,
        )


def test_native_response_without_final_message_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response_data = {
        "output": [{"type": "reasoning", "content": "No answer yet."}],
        "stats": {"reasoning_output_tokens": 10},
    }
    _, events = _capture_transport(monkeypatch, response_data)

    with pytest.raises(ValueError, match="no answer text"):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/api/v1/chat",
            model="local-model",
            reasoning="off",
        )

    assert events == []


def test_native_reasoning_rejection_surfaces_provider_error_without_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, events = _capture_transport(
        monkeypatch,
        {"error": {"message": "Reasoning option off is unsupported."}},
        status_code=400,
    )

    with pytest.raises(ValueError, match="Reasoning option off is unsupported"):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/api/v1/chat",
            model="local-model",
            reasoning="off",
        )

    assert len(calls) == 1
    assert calls[0]["json"]["reasoning"] == "off"
    assert events == []


def test_relative_endpoint_uses_the_resolver_and_proxy_transport_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    resolved: list[str] = []
    option_urls: list[str] = []

    def resolve(url: str) -> str:
        resolved.append(url)
        return "http://127.0.0.1:8188/lf-nodes/proxy/local"

    def options(url: str, headers: dict) -> dict:
        option_urls.append(url)
        assert headers == {"Content-Type": "application/json"}
        return {
            "headers": {
                **headers,
                "X-LF-Proxy-Secret": "test-only-secret",
            },
            "allow_redirects": False,
        }

    monkeypatch.setattr(transport_module, "resolve_api_url", resolve)
    monkeypatch.setattr(
        transport_module,
        "local_proxy_request_options",
        options,
    )
    calls, _ = _capture_transport(monkeypatch)

    result = chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Prompt",
        url="/lf-nodes/proxy/local",
    )

    assert resolved == ["/lf-nodes/proxy/local"]
    assert option_urls == ["/lf-nodes/proxy/local"]
    assert calls[0]["url"] == (
        "http://127.0.0.1:8188/lf-nodes/proxy/local"
    )
    assert calls[0]["headers"]["X-LF-Proxy-Secret"] == (
        "test-only-secret"
    )
    assert calls[0]["allow_redirects"] is False
    assert "test-only-secret" not in json.dumps(result)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"prompt": "", "url": "http://localhost.test"}, "Prompt"),
        ({"prompt": "Prompt", "url": "  "}, "URL"),
        (
            {
                "prompt": "Prompt",
                "url": "http://localhost.test",
                "max_tokens": 0,
            },
            "max_tokens",
        ),
        (
            {
                "prompt": "Prompt",
                "url": "http://localhost.test",
                "timeout": 0,
            },
            "timeout",
        ),
    ],
)
def test_invalid_input_fails_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    kwargs: dict,
    message: str,
) -> None:
    def unexpected_post(*_args, **_kwargs):
        pytest.fail("Invalid input must fail before transport.")

    monkeypatch.setattr(transport_module.requests, "post", unexpected_post)

    with pytest.raises(ValueError, match=message):
        chat_module.LF_LocalChatCompletions().on_exec(**kwargs)


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        (
            "temperature",
            True,
            "temperature must be a finite number between 0 and 2.",
        ),
        (
            "temperature",
            float("nan"),
            "temperature must be a finite number between 0 and 2.",
        ),
        (
            "temperature",
            float("inf"),
            "temperature must be a finite number between 0 and 2.",
        ),
        (
            "temperature",
            "hot",
            "temperature must be a finite number between 0 and 2.",
        ),
        (
            "temperature",
            -0.01,
            "temperature must be a finite number between 0 and 2.",
        ),
        (
            "temperature",
            2.01,
            "temperature must be a finite number between 0 and 2.",
        ),
        ("max_tokens", False, "max_tokens must be a positive integer."),
        (
            "max_tokens",
            float("nan"),
            "max_tokens must be a positive integer.",
        ),
        (
            "max_tokens",
            float("-inf"),
            "max_tokens must be a positive integer.",
        ),
        ("max_tokens", "many", "max_tokens must be a positive integer."),
        ("max_tokens", 1.5, "max_tokens must be a positive integer."),
        ("max_tokens", -1, "max_tokens must be a positive integer."),
        ("timeout", True, "timeout must be a positive integer."),
        (
            "timeout",
            float("nan"),
            "timeout must be a positive integer.",
        ),
        (
            "timeout",
            float("inf"),
            "timeout must be a positive integer.",
        ),
        ("timeout", [], "timeout must be a positive integer."),
        ("timeout", "1.5", "timeout must be a positive integer."),
        ("timeout", 0, "timeout must be a positive integer."),
    ],
)
def test_numeric_inputs_are_validated_before_transport(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: object,
    message: str,
) -> None:
    def unexpected_post(*_args, **_kwargs):
        pytest.fail("Invalid numeric input must fail before transport.")

    monkeypatch.setattr(transport_module.requests, "post", unexpected_post)
    kwargs = {
        "prompt": "Prompt",
        "url": "http://localhost.test/v1/chat/completions",
        name: value,
    }

    with pytest.raises(ValueError) as raised:
        chat_module.LF_LocalChatCompletions().on_exec(**kwargs)

    assert str(raised.value) == message


def test_numeric_inputs_accept_published_boundaries_and_exact_integers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls, _ = _capture_transport(monkeypatch)

    chat_module.LF_LocalChatCompletions().on_exec(
        prompt="Prompt",
        url="http://localhost.test/v1/chat/completions",
        temperature=2,
        max_tokens=1.0,
        timeout="30",
    )

    assert calls[0]["json"]["temperature"] == 2.0
    assert calls[0]["json"]["max_tokens"] == 1
    assert calls[0]["timeout"] == 30


@pytest.mark.parametrize("status_code", (400, 401, 403, 429, 500, 503))
def test_http_errors_fail_without_publishing_success(
    monkeypatch: pytest.MonkeyPatch,
    status_code: int,
) -> None:
    calls, events = _capture_transport(
        monkeypatch,
        {"error": "provider detail"},
        status_code=status_code,
    )

    with pytest.raises(ValueError) as raised:
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    assert str(raised.value) == (
        "Local chat-completions request failed with HTTP status "
        f"{status_code}. Provider said: provider detail"
    )
    assert len(calls) == 1
    assert events == []


def test_openai_error_envelope_is_bounded_and_surfaced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider_message = "No models loaded. " + ("x" * 600)
    _, events = _capture_transport(
        monkeypatch,
        {"error": {"message": provider_message}},
        status_code=400,
    )

    with pytest.raises(ValueError) as raised:
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    message = str(raised.value)
    assert message.startswith(
        "Local chat-completions request failed with HTTP status 400. "
        "Provider said: No models loaded. "
    )
    assert message.endswith("...")
    assert len(message.removeprefix(
        "Local chat-completions request failed with HTTP status 400. Provider said: "
    )) == transport_module._MAX_UPSTREAM_ERROR_CHARS
    assert events == []


def test_non_json_http_error_keeps_stable_status_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, events = _capture_transport(
        monkeypatch,
        ValueError("not json"),
        status_code=502,
    )

    with pytest.raises(ValueError) as raised:
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    assert str(raised.value) == (
        "Local chat-completions request failed with HTTP status 502."
    )
    assert events == []


def test_non_json_response_fails_without_publishing_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, events = _capture_transport(
        monkeypatch,
        ValueError("not json"),
    )

    with pytest.raises(ValueError, match="not valid JSON"):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    assert events == []


def test_non_object_json_response_fails_without_publishing_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, events = _capture_transport(monkeypatch, ["not", "an", "object"])

    with pytest.raises(ValueError, match="must be a JSON object"):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    assert events == []


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (
            {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": ""},
                    }
                ]
            },
            "exhausted its response token budget",
        ),
        (
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": ""},
                    }
                ]
            },
            "no answer text",
        ),
    ],
)
def test_missing_answer_text_fails_without_publishing_success(
    monkeypatch: pytest.MonkeyPatch,
    data: dict,
    message: str,
) -> None:
    _, events = _capture_transport(monkeypatch, data)

    with pytest.raises(ValueError, match=message):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    assert events == []


def test_transport_error_is_stable_and_does_not_publish_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[tuple] = []

    def fail(*_args, **_kwargs):
        raise requests.ConnectionError("provider-specific detail")

    monkeypatch.setattr(transport_module.requests, "post", fail)
    monkeypatch.setattr(
        chat_module,
        "safe_send_sync",
        lambda *args: events.append(args),
    )

    with pytest.raises(
        ValueError,
        match="whether the local model server is running",
    ):
        chat_module.LF_LocalChatCompletions().on_exec(
            prompt="Prompt",
            url="http://localhost.test/v1/chat/completions",
        )

    assert events == []
