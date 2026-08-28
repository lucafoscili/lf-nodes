from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace

import pytest


@pytest.fixture
def safe_send_module(monkeypatch: pytest.MonkeyPatch):
    sent: list[tuple] = []
    server = types.ModuleType("server")
    server.PromptServer = SimpleNamespace(
        instance=SimpleNamespace(
            client_id="client-a",
            send_sync=lambda *args: sent.append(args),
        )
    )
    monkeypatch.setitem(sys.modules, "server", server)
    module = importlib.import_module(
        "modules.utils.helpers.comfy.safe_send_sync"
    )
    yield module, server.PromptServer.instance, sent


def test_safe_send_sync_targets_the_current_prompt_owner(safe_send_module) -> None:
    module, _server, sent = safe_send_module

    module.safe_send_sync("example", {"value": "ready"}, [["73"]])

    assert sent == [
        (
            "lf-example",
            {"value": "ready", "node": "73"},
            "client-a",
        )
    ]


def test_safe_send_sync_broadcasts_only_without_a_current_owner(
    safe_send_module,
) -> None:
    module, server, sent = safe_send_module
    server.client_id = None

    module.safe_send_sync("example", {"value": "headless"}, "73")

    assert sent == [
        (
            "lf-example",
            {"value": "headless", "node": "73"},
        )
    ]


def test_explicit_target_cannot_be_retargeted_by_a_later_prompt(
    safe_send_module,
) -> None:
    module, server, sent = safe_send_module
    captured_client_id = module.get_current_client_id()
    server.client_id = "client-b"

    module.safe_send_sync(
        "example",
        {"value": "async-ready"},
        "73",
        target_client_id=captured_client_id,
    )

    assert sent == [
        (
            "lf-example",
            {"value": "async-ready", "node": "73"},
            "client-a",
        )
    ]


def test_explicit_headless_target_does_not_adopt_a_later_prompt_owner(
    safe_send_module,
) -> None:
    module, server, sent = safe_send_module
    server.client_id = None
    captured_client_id = module.get_current_client_id()
    server.client_id = "client-b"

    module.safe_send_sync(
        "example",
        {"value": "headless-ready"},
        "73",
        target_client_id=captured_client_id,
    )

    assert sent == [
        (
            "lf-example",
            {"value": "headless-ready", "node": "73"},
        )
    ]
