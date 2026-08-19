"""Negative-path tests for unknown or invalid workflow IDs."""

import pytest
import sys

from pathlib import Path

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

pytestmark = pytest.mark.anyio

def test_prepare_workflow_unknown_id(monkeypatch):
    comfy_root = pkg_root.parents[1]
    if str(comfy_root) not in sys.path:
        sys.path.insert(0, str(comfy_root))

    from modules.workflow_runner.services import executor

    monkeypatch.setattr(executor, "get_workflow", lambda _workflow_id: None)

    payload = {"workflowId": "does-not-exist", "inputs": {}}
    with pytest.raises(executor.WorkflowPreparationError) as exc:
        executor._prepare_workflow_execution(payload)

    err = exc.value
    assert getattr(err, "status", None) == 404
    body = getattr(err, "response_body", {})
    assert body.get("payload", {}).get("error", {}).get("message") == "unknown_workflow"
