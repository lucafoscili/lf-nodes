import pytest
import json
import sys

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

# make package imports work
pkg_root = Path(__file__).resolve().parents[3]
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

# Mock heavy top-level modules that aren't available in the test environment
from unittest.mock import Mock
sys.modules['execution'] = Mock()
sys.modules['server'] = Mock()
sys.modules['server'].PromptServer = Mock()

# Some import paths pull heavy GPU-related modules (torch.cuda) at import time
# which raise on machines without CUDA support. If that happens, skip these
# tests gracefully so the CI/dev run stays stable on CPU-only environments.
try:
    from modules.workflow_runner.controllers import api_controllers
    from modules.workflow_runner.services import job_store, lifecycle
except AssertionError as e:
    pytest.skip(f"Skipping SSE snapshot payload tests due to import error: {e}", allow_module_level=True)

pytestmark = pytest.mark.anyio

class FakeResponse:
    def __init__(self):
        self.written = []

    async def write(self, data: bytes):
        # collect bytes for inspection
        self.written.append(data)

    async def drain(self):
        return None

async def test_send_initial_snapshot_includes_workflow_id_and_updated_at():
    # create a Job instance to be returned by job_store.list_jobs
    job = job_store.Job(id="r1", workflow_id="remove_bg")
    # populate updated_at so snapshot includes it
    job.updated_at = 1234567.89
    job.seq = 2

    async def fake_list_jobs(owner_id=None):
        return {job.id: job}

    resp = FakeResponse()

    with patch.object(job_store, 'list_jobs', side_effect=fake_list_jobs):
        # Call the internal snapshot sender
        await api_controllers._send_initial_snapshot(resp, subscriber_owner=None, last_event=None)

    # Combine written payloads and decode
    combined = b''.join(resp.written).decode('utf-8')
    # Expect workflow_id and updated_at present in the JSON payload
    assert '"workflow_id": "remove_bg"' in combined
    assert '"updated_at":' in combined


async def test_sse_snapshot_restores_stable_submission_control_handle():
    job = job_store.Job(
        id="run-sse-control",
        workflow_id="remove_bg",
        status=job_store.JobStatus.RUNNING,
    )
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "lf-web:sse-control",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "remove_bg")
    await lifecycle.bind_prompt(
        "lf-web:sse-control",
        "run-sse-control",
        "http://comfy:8188",
    )

    resp = FakeResponse()
    with patch.object(job_store, "list_jobs", return_value={job.id: job}):
        await api_controllers._send_initial_snapshot(resp, summary_only=True)

    data_line = next(
        line
        for line in b"".join(resp.written).decode("utf-8").splitlines()
        if line.startswith("data: ")
    )
    event = json.loads(data_line.removeprefix("data: "))
    assert event["submission_id"] == "lf-web:sse-control"
    assert event["cancel_requested"] is False


async def test_history_and_sse_preserve_terminal_results_by_default_and_bound_on_opt_in():
    job = job_store.Job(
        id="terminal-compat",
        workflow_id="portrait",
        status=job_store.JobStatus.SUCCEEDED,
        result={
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {
                                        "filename": "portrait.png",
                                        "subfolder": "",
                                        "type": "output",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        },
    )

    async def fake_list_jobs(owner_id=None, status=None):
        return {job.id: job}

    with patch.object(job_store, "list_jobs", side_effect=fake_list_jobs):
        legacy_response = await api_controllers.list_runs_controller(
            SimpleNamespace(query={})
        )
        summary_response = await api_controllers.list_runs_controller(
            SimpleNamespace(query={"summary": "1"})
        )

    legacy_run = json.loads(legacy_response.text)["runs"][0]
    summary_run = json.loads(summary_response.text)["runs"][0]
    assert legacy_run["result"] == job.result
    assert "result" not in summary_run
    assert summary_run["outputs"]["save"]["images"][0]["filename"] == "portrait.png"

    legacy_sse = FakeResponse()
    summary_sse = FakeResponse()
    with patch.object(job_store, "list_jobs", side_effect=fake_list_jobs):
        await api_controllers._send_initial_snapshot(
            legacy_sse,
            summary_only=False,
        )
        await api_controllers._send_initial_snapshot(
            summary_sse,
            summary_only=True,
        )

    def first_event(response: FakeResponse) -> dict:
        data_line = next(
            line
            for line in b"".join(response.written).decode("utf-8").splitlines()
            if line.startswith("data: ")
        )
        return json.loads(data_line.removeprefix("data: "))

    assert first_event(legacy_sse)["result"] == job.result
    assert "result" not in first_event(summary_sse)
