"""Isolated behavior tests for LF frontend event delivery."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "modules" / "utils" / "helpers" / "comfy" / "safe_send_sync.py"


def _attach(name: str, module: ModuleType) -> ModuleType:
    sys.modules[name] = module
    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent = sys.modules.get(parent_name)
        if parent is not None:
            setattr(parent, child_name, module)
    return module


def _package(name: str) -> ModuleType:
    package = ModuleType(name)
    package.__path__ = []
    return _attach(name, package)


def _load_harness():
    prefix = f"_lf_safe_send_{uuid.uuid4().hex}"
    _package(prefix)
    _package(f"{prefix}.utils")
    _package(f"{prefix}.utils.helpers")
    _package(f"{prefix}.utils.helpers.comfy")

    constants = ModuleType(f"{prefix}.utils.constants")
    constants.EVENT_PREFIX = "lf-"
    _attach(constants.__name__, constants)

    sent = []

    class Recorder:
        def send_sync(self, event, payload):
            sent.append((event, payload))

    server = ModuleType("server")
    server.PromptServer = SimpleNamespace(instance=Recorder())
    previous_server = sys.modules.get("server")
    sys.modules["server"] = server

    module_name = f"{prefix}.utils.helpers.comfy.safe_send_sync"
    spec = importlib.util.spec_from_file_location(module_name, SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    _attach(module_name, module)
    spec.loader.exec_module(module)
    return module, sent, server, previous_server


def _restore_server(previous_server) -> None:
    if previous_server is None:
        sys.modules.pop("server", None)
    else:
        sys.modules["server"] = previous_server


def test_event_prefix_nested_list_node_id_and_payload_copy() -> None:
    module, sent, _server, previous_server = _load_harness()
    payload = {"value": "ready", "node": "caller-owned"}
    try:
        module.safe_send_sync("preview", payload, [[("node-17",)]])
    finally:
        _restore_server(previous_server)

    assert payload == {"value": "ready", "node": "caller-owned"}
    assert sent == [("lf-preview", {"value": "ready", "node": "node-17"})]


def test_empty_node_id_omits_node_key() -> None:
    module, sent, _server, previous_server = _load_harness()
    try:
        module.safe_send_sync("preview", {"value": "ready"}, [[]])
    finally:
        _restore_server(previous_server)

    assert sent == [("lf-preview", {"value": "ready"})]


def test_numeric_zero_node_id_is_preserved() -> None:
    module, sent, _server, previous_server = _load_harness()
    try:
        module.safe_send_sync("preview", {"value": "ready"}, 0)
    finally:
        _restore_server(previous_server)

    assert sent == [("lf-preview", {"value": "ready", "node": 0})]


def test_missing_or_failing_websocket_is_nonfatal() -> None:
    module, _sent, server, previous_server = _load_harness()

    class FailingRecorder:
        def send_sync(self, _event, _payload):
            raise RuntimeError("socket unavailable")

    try:
        server.PromptServer.instance = None
        module.safe_send_sync("preview", {"value": "headless"}, "node-1")
        server.PromptServer.instance = FailingRecorder()
        module.safe_send_sync("preview", {"value": "headless"}, "node-1")
    finally:
        _restore_server(previous_server)
