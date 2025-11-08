"""Negative test: non-dict inputs should raise WorkflowPreparationError (400)."""

import sys
from pathlib import Path
import pytest

pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

pytestmark = pytest.mark.anyio

async def test_invalid_inputs_type():
    from modules.workflow_runner.services.executor import _prepare_workflow_execution, WorkflowPreparationError
    bad_payload = {"workflowId": "wf-any", "inputs": ["not", "a", "dict"]}
    with pytest.raises(WorkflowPreparationError) as exc:
        _prepare_workflow_execution(bad_payload)
    err = exc.value
    assert err.status == 400
    assert err.response_body["payload"]["error"]["message"] == "invalid_inputs"