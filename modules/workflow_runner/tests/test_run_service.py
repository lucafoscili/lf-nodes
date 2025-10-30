"""Basic tests for run_service scaffold."""
import asyncio

from ..services.run_service import run_workflow
from ..models.schemas import StartWorkflowSchema


def test_run_workflow_returns_stub(loop=asyncio.get_event_loop()):
    schema = StartWorkflowSchema(name="test")
    result = loop.run_until_complete(run_workflow(schema))
    assert isinstance(result, dict)
    assert result.get("run_id") == "stub-run-id"
