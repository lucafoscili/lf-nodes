from __future__ import annotations

import importlib

import pytest

from modules.utils.constants import HEADERS


auth = importlib.import_module("modules.utils.helpers.api.lm_studio_auth")
chat = importlib.import_module("modules.utils.helpers.api.local_chat_completion")
models = importlib.import_module("modules.utils.helpers.api.lm_studio_models")
lifecycle = importlib.import_module("modules.utils.helpers.api.lm_studio_lifecycle")
URL = "http://localhost.test/api/v1/chat"


class Response:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data


@pytest.fixture(autouse=True)
def clear_token_environment(monkeypatch):
    monkeypatch.delenv("LM_API_TOKEN", raising=False)
    monkeypatch.delenv("LM_API_TOKEN_FILE", raising=False)


def test_auth_copies_headers_and_preserves_proxy_options(monkeypatch):
    monkeypatch.setenv("LM_API_TOKEN", "native-secret")
    headers_before = dict(HEADERS)
    original = {"headers": {**HEADERS, "X-LF-Proxy-Secret": "proxy-secret"}, "allow_redirects": False}
    authenticated, token = auth.with_lm_studio_auth(original)
    assert token == "native-secret"
    assert authenticated == {
        "headers": {**original["headers"], "Authorization": "Bearer native-secret"},
        "allow_redirects": False,
    }
    assert "Authorization" not in original["headers"]
    assert HEADERS == headers_before


def test_no_token_preserves_original_transport_semantics():
    original = {"headers": HEADERS}
    result, token = auth.with_lm_studio_auth(original)
    assert result == original
    assert result["headers"] is not HEADERS
    assert token is None
    assert "allow_redirects" not in result


@pytest.mark.parametrize("token_source", ["environment", "file"])
def test_discovery_and_native_chat_share_server_auth(monkeypatch, tmp_path, token_source):
    if token_source == "environment":
        monkeypatch.setenv("LM_API_TOKEN", "native-secret")
    else:
        token_file = tmp_path / "lm-token.txt"
        token_file.write_text("native-secret\n", encoding="utf-8")
        monkeypatch.setenv("LM_API_TOKEN_FILE", str(token_file))
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        return Response({"models": [{"type": "llm", "loaded_instances": [{"id": "mine"}]}]})

    def post(url, **kwargs):
        calls.append((url, kwargs))
        return Response({"output": [{"type": "message", "content": "Done"}]})

    monkeypatch.setattr(chat.requests, "get", get)
    monkeypatch.setattr(chat.requests, "post", post)
    before = dict(HEADERS)
    assert chat.request_local_chat_completion("Prompt", URL)[0] == "Done"
    assert len(calls) == 2
    assert calls[0][0] == "http://localhost.test/api/v1/models"
    assert calls[1][0] == URL
    for _, options in calls:
        assert options["headers"]["Authorization"] == "Bearer native-secret"
        assert options["allow_redirects"] is False
        assert "native-secret" not in str(options.get("json"))
    assert HEADERS == before


def test_generic_chat_never_reads_or_sends_lm_secret(monkeypatch):
    monkeypatch.setenv("LM_API_TOKEN", "native-secret")
    monkeypatch.setattr(auth, "read_secret", lambda _name: pytest.fail("Generic endpoint must not read LM auth"))
    calls = []

    def post(url, **options):
        calls.append(options)
        return Response({"choices": [{"message": {"content": "Done"}}]})

    monkeypatch.setattr(chat.requests, "post", post)
    assert chat.request_local_chat_completion("Prompt", "http://localhost.test/v1/chat/completions")[0] == "Done"
    assert calls[0]["headers"] == HEADERS
    assert "allow_redirects" not in calls[0]


def test_native_proxy_retains_its_own_auth_boundary(monkeypatch):
    monkeypatch.setenv("LM_API_TOKEN", "native-secret")
    monkeypatch.setenv("LF_PROXY_SECRET", "proxy-secret")
    calls = []

    def post(url, **options):
        calls.append(options)
        return Response({"output": [{"type": "message", "content": "Done"}]})

    monkeypatch.setattr(chat.requests, "post", post)
    chat.request_local_chat_completion("Prompt", "/lf-nodes/proxy/lms/api/v1/chat", model="mine")
    assert calls[0]["headers"] == {
        **HEADERS,
        "X-LF-Proxy-Secret": "proxy-secret",
        "Authorization": "Bearer native-secret",
    }
    assert calls[0]["allow_redirects"] is False


@pytest.mark.parametrize("stage", ["discovery", "chat", "lifecycle"])
@pytest.mark.parametrize("prefix", ["", "x" * 485])
def test_provider_errors_redact_before_bounding(monkeypatch, stage, prefix):
    secret = "secret-that-must-not-be-partly-visible"
    monkeypatch.setenv("LM_API_TOKEN", secret)
    response = Response({"error": {"message": prefix + secret + " denied " + "z" * 600}}, 401)
    monkeypatch.setattr(chat.requests, "get", lambda *_args, **_kwargs: response)
    monkeypatch.setattr(chat.requests, "post", lambda *_args, **_kwargs: response)
    with pytest.raises(ValueError) as error:
        if stage == "discovery":
            models.resolve_loaded_lm_studio_llm(URL, 120)
        elif stage == "chat":
            chat.request_local_chat_completion("Prompt", URL, model="mine")
        else:
            lifecycle.load_lm_studio_model("mine", URL)
    message = str(error.value)
    assert secret not in message
    assert secret[:10] not in message
    assert "[redacted]" in message
    assert "HTTP status 401" in message
    detail = message.split("Provider said: ", 1)[1]
    assert len(detail) == 500
    assert detail.endswith("...")
