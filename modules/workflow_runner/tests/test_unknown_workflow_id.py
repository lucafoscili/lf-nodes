"""Negative-path tests for unknown or invalid workflow IDs."""

import sys
from pathlib import Path
import pytest

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

pytestmark = pytest.mark.anyio


def test_prepare_workflow_unknown_id():
    from modules.workflow_runner.services.executor import _prepare_workflow_execution, WorkflowPreparationError

    payload = {"workflowId": "does-not-exist", "inputs": {}}
    with pytest.raises(WorkflowPreparationError) as exc:
        _prepare_workflow_execution(payload)

    err = exc.value
    assert getattr(err, "status", None) == 404
    body = getattr(err, "response_body", {})
    assert body.get("payload", {}).get("error", {}).get("message") == "unknown_workflow"
